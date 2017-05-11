/**
 * Function from: https://gist.github.com/talos/50000ed856eb688c66b10d1054a9bcc6
 * Add all functions below to be able to augment your CARTO table
 * with several measurements at once.
 *
 * `obs_meta_table` and `obs_data_table` are more internally focused,
 * although you could use the latter to work more flexibly with the
 * data without altering any of your user tables.
 **/

/** Example usage:

-- Copy all code starting with `CREATE OR REPLACE FUNCTION` in this file
-- into any CARTO table's SQL pane and execute.  That will not alter
-- your table.

-- With an existing CARTO table with geometries called `my_sample_table`,
-- run the query immediately below this.  Remember to include your user
-- name if you're running this in a team account.

-- This will add total population ('us.census.acs.B01003001')
-- and total households ('us.census.acs.B11001001') to your table.

SELECT obs_augment_table('my_user_name.my_sample_table',
                         '[{"numer_id": "us.census.acs.B01003001", "normalization": "predenom"},
                           {"numer_id": "us.census.acs.B11001001", "normalization": "predenom"}]')

-- Once the query is run it will have two new columns, `total_pop_predenom_2011_2015`
-- and `households_predenom_2011_2015`.

*/

CREATE OR REPLACE FUNCTION obs_meta_table(
  tablename REGCLASS,
  input_meta JSON,
  id_col TEXT DEFAULT 'cartodb_id',
  geom_col TEXT DEFAULT 'the_geom'
) RETURNS TABLE (
  extent Geometry(Geometry, 4326),
  output_meta JSON,
  geomvals Geomval[],
  sumarea Numeric
)
AS $$
DECLARE
  extent Geometry(Geometry, 4326);
  geomvals Geomval[];
  rowcount BIGINT;
  output_meta JSON;
  sumarea Numeric;
BEGIN

  -- Useful summary data about the table
  EXECUTE format($query$
    SELECT ST_SetSRID(ST_Extent(%I), 4326) extent,
           COUNT(*) rowcount,
           ARRAY_AGG((%I, %I::INT)::geomval) geomvals,
           SUM(ST_Area(%I)) sumarea
    FROM %I
  $query$, geom_col, geom_col, id_col, geom_col, tablename)
  INTO extent, rowcount, geomvals, sumarea;

  -- Set target_area to the same value on each input_meta element
  EXECUTE $query$
    SELECT JSON_Agg(jsonb_set)
    FROM (SELECT JSONB_Set(JSONB_Array_elements($1::JSONB), '{target_area}', $2::TEXT::JSONB)) foo
  $query$
  INTO input_meta
  USING input_meta, sumarea;

  -- Obtain metadata using summary data
  EXECUTE $query$
    SELECT cdb_dataservices_client.OBS_GetMeta($1, $2, 1, 1, $3::INT)
  $query$
  INTO output_meta
  USING extent, input_meta, rowcount;

  RETURN QUERY SELECT extent, output_meta, geomvals, sumarea;
  RETURN;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION obs_data_table(
  tablename REGCLASS,
  input_meta JSON,
  keep_geoms BOOLEAN DEFAULT TRUE,
  id_col TEXT DEFAULT 'cartodb_id',
  geom_col TEXT DEFAULT 'the_geom'
) RETURNS TABLE (
  id BIGINT,
  data JSON
)
AS $$
DECLARE
  extent Geometry(Geometry, 4326);
  geomvals Geomval[];
  output_meta JSON;
  sumarea Numeric;
BEGIN
  -- Obtain summary data & metadata
  EXECUTE $query$ SELECT * FROM obs_meta_table($1, $2, $3, $4) $query$
  INTO extent, output_meta, geomvals, sumarea
  USING tablename, input_meta, id_col, geom_col;

  -- Obtain actual data
  RETURN QUERY EXECUTE $query$
    SELECT id::BIGINT, data
    FROM cdb_dataservices_client.OBS_GetData($1, $2, $3)
  $query$
  USING geomvals, output_meta, keep_geoms;
  RETURN;
END;
$$ LANGUAGE plpgsql STABLE;


CREATE OR REPLACE FUNCTION obs_augment_table(
  tablename REGCLASS,
  input_meta JSON,
  id_col TEXT DEFAULT 'cartodb_id',
  geom_col TEXT DEFAULT 'the_geom'
) RETURNS JSON
AS $$
DECLARE
  extent Geometry(Geometry, 4326);
  geomvals Geomval[];
  output_meta JSON;
  alter_column_stmt TEXT;
  update_stmt TEXT;
  rowcount BIGINT;
BEGIN
  -- Obtain summary data & metadata
  EXECUTE $query$ SELECT * FROM obs_meta_table($1, $2, $3, $4) $query$
  INTO extent, output_meta, geomvals
  USING tablename, input_meta, id_col, geom_col;

  RAISE NOTICE '%', output_meta;

  -- Build alter column and update statements
  EXECUTE $query$
  WITH meta AS (
    SELECT JSON_Array_Elements(output_meta)->>'numer_type' numer_type,
           JSON_Array_Elements(output_meta)->>'numer_colname' numer_colname,
           JSON_Array_Elements(output_meta)->>'numer_name' numer_name,
           JSON_Array_Elements(output_meta)->>'normalization' normalization,
           JSON_Array_Elements(output_meta)->>'numer_timespan' numer_timespan
    FROM obs_meta_table($1, $2, $3, $4)
  ),
  coldefs AS (SELECT
    '"' || numer_colname || '_' ||
      COALESCE(normalization || '_', '') ||
      REPLACE(numer_timespan, ' - ', '_') || '"' AS colname,
      numer_type AS coltype,
      ROW_NUMBER() OVER () - 1 rownumber
    FROM meta
  )
  SELECT 'ALTER TABLE ' || $1 || ' ' ||
    STRING_AGG('ADD ' || colname || ' ' || coltype , ', ') AS altercol,
    'UPDATE ' || $1 || ' ' || ' SET ' ||
    STRING_AGG(colname || ' = (_data.data->' || rownumber::text || '->>''value'')::' || coltype, ', ') ||
    ' FROM cdb_dataservices_client.OBS_GetData($1, $2) _data' ||
    ' WHERE _data.id = ' || $1 || '.' || $3
    AS update_stmt
  FROM coldefs
  $query$
  INTO alter_column_stmt, update_stmt
  USING tablename, input_meta, id_col, geom_col;

  EXECUTE alter_column_stmt;
  EXECUTE update_stmt USING geomvals, output_meta;

  RETURN output_meta;
END;
$$ LANGUAGE plpgsql VOLATILE;
