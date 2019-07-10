from .dataset_base import DatasetBase


class DataFrameDataset(DatasetBase):
    def __init__(self, data):
        super(DataFrameDataset, self).__init__()
        self._state = DatasetBase.STATE_LOCAL

        self._df = data

    def download(self):
        raise ValueError('It is not possible to download a DataFrameDataset')

    def upload(self, with_lnglat, if_exists):
        self._is_ready_for_upload_validation()

        if if_exists == DatasetBase.REPLACE or not self.exists():
            self._create_table(with_lnglat)
            # if if_exists != DatasetBase.APPEND:
            #     self._is_saved_in_carto = True
        elif if_exists == DatasetBase.FAIL:
            raise self._already_exists_error()

        self._copyfrom(with_lnglat)

    def _copyfrom(self, with_lnglat):
        geom_col = _get_geom_col_name(self._df)
        enc_type = _detect_encoding_type(self._df, geom_col)
        columns = ','.join(norm for norm, orig in _normalize_column_names(self._df))

        query = """COPY {table_name}({columns},the_geom) FROM stdin WITH (FORMAT csv, DELIMITER '|');""".format(
            table_name=self._table_name,
            columns=columns)

        data = _rows(
            self._df,
            [c for c in self._df.columns if c != 'cartodb_id'],
            with_lnglat,
            geom_col,
            enc_type)

        self._client.upload(query, data)


def _rows(df, cols, with_lnglat, geom_col, enc_type):
    for i, row in df.iterrows():
        csv_row = ''
        the_geom_val = None
        lng_val = None
        lat_val = None
        for col in cols:
            if with_lnglat and col in Column.SUPPORTED_GEOM_COL_NAMES:
                continue
            val = row[col]
            if _is_null(val):
                val = ''
            if with_lnglat:
                if col == with_lnglat[0]:
                    lng_val = row[col]
                if col == with_lnglat[1]:
                    lat_val = row[col]
            if col == geom_col:
                the_geom_val = row[col]
            else:
                csv_row += '{val}|'.format(val=val)

        if the_geom_val is not None:
            geom = decode_geometry(the_geom_val, enc_type)
            if geom:
                csv_row += 'SRID=4326;{geom}'.format(geom=geom.wkt)
        if with_lnglat is not None and lng_val is not None and lat_val is not None:
            csv_row += 'SRID=4326;POINT({lng} {lat})'.format(lng=lng_val, lat=lat_val)

        csv_row += '\n'
        yield csv_row.encode()


def _is_null(val):
    vnull = pd.isnull(val)
    if isinstance(vnull, bool):
        return vnull
    else:
        return vnull.all()


def _normalize_column_names(df):
    column_names = [c for c in df.columns if c not in Column.RESERVED_COLUMN_NAMES]
    normalized_columns = normalize_names(column_names)

    column_tuples = [(norm, orig) for orig, norm in zip(column_names, normalized_columns)]

    changed_cols = '\n'.join([
        '\033[1m{orig}\033[0m -> \033[1m{new}\033[0m'.format(
            orig=orig,
            new=norm)
        for norm, orig in column_tuples if norm != orig])

    if changed_cols != '':
        tqdm.write('The following columns were changed in the CARTO '
                   'copy of this dataframe:\n{0}'.format(changed_cols))

    return column_tuples


def _get_geom_col_name(df):
    geom_col = getattr(df, '_geometry_column_name', None)
    if geom_col is None:
        try:
            geom_col = next(x for x in df.columns if x.lower() in Column.SUPPORTED_GEOM_COL_NAMES)
        except StopIteration:
            pass

    return geom_col


def _detect_encoding_type(df, geom_col):
    if geom_col is not None:
        first_geom = _first_value(df[geom_col])
        if first_geom:
            return detect_encoding_type(first_geom)
    return ''
