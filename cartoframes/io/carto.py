"""Functions to interact with the CARTO platform"""
import math

from pandas import DataFrame
from geopandas import GeoDataFrame

from carto.exceptions import CartoException

from .managers.context_manager import ContextManager, _compute_copy_data, get_dataframe_columns_info
from ..utils.geom_utils import is_reprojection_needed, reproject, has_geometry, set_geometry
from ..utils.logger import log
from ..utils.utils import is_valid_str, is_sql_query
from ..utils.metrics import send_metrics


GEOM_COLUMN_NAME = 'the_geom'
IF_EXISTS_OPTIONS = ['fail', 'replace', 'append']

MAX_UPLOAD_SIZE_BYTES = 2000000000  # 2GB
SAMPLE_ROWS_NUMBER = 100
CSV_TO_CARTO_RATIO = 1.4


@send_metrics('data_downloaded')
def read_carto(source, credentials=None, limit=None, retry_times=3, schema=None, index_col=None, decode_geom=True,
               null_geom_value=None):
    """Read a table or a SQL query from the CARTO account.

    Args:
        source (str): table name or SQL query.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        limit (int, optional):
            The number of rows to download. Default is to download all rows.
        retry_times (int, optional):
            Number of time to retry the download in case it fails. Default is 3.
        schema (str, optional): prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
        index_col (str, optional): name of the column to be loaded as index. It can be used also to set the index name.
        decode_geom (bool, optional): convert the "the_geom" column into a valid geometry column.
        null_geom_value (Object, optional): value for the `the_geom` column when it's null.
            Defaults to None

    Returns:
        geopandas.GeoDataFrame

    Raises:
        ValueError: if the source is not a valid table_name or SQL query.

    """
    if not is_valid_str(source):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')

    context_manager = ContextManager(credentials)

    df = context_manager.copy_to(source, schema, limit, retry_times)

    gdf = GeoDataFrame(df)

    if index_col:
        if index_col in gdf:
            gdf.set_index(index_col, inplace=True)
        else:
            gdf.index.name = index_col

    if decode_geom and GEOM_COLUMN_NAME in gdf:
        # Decode geometry column
        set_geometry(gdf, GEOM_COLUMN_NAME, inplace=True, crs='epsg:4326')

        if null_geom_value is not None:
            gdf[GEOM_COLUMN_NAME].fillna(null_geom_value, inplace=True)

    return gdf


@send_metrics('data_uploaded')
def to_carto(dataframe, table_name, credentials=None, if_exists='fail', geom_col=None, index=False, index_label=None,
             cartodbfy=True, log_enabled=True, retry_times=3, max_upload_size=MAX_UPLOAD_SIZE_BYTES,
             skip_quota_warning=False):
    """Upload a DataFrame to CARTO. The geometry's CRS must be WGS 84 (EPSG:4326) so you can use it on CARTO.

    Args:
        dataframe (pandas.DataFrame, geopandas.GeoDataFrame`): data to be uploaded.
        table_name (str): name of the table to upload the data.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.
        geom_col (str, optional): name of the geometry column of the dataframe.
        index (bool, optional): write the index in the table. Default is False.
        index_label (str, optional): name of the index column in the table. By default it
            uses the name of the index from the dataframe.
        cartodbfy (bool, optional): convert the table to CARTO format. Default True. More info
            `here <https://carto.com/developers/sql-api/guides/creating-tables/#create-tables>`.
        log_enabled (bool, optional): enable the logging mechanism. Default is True.
        retry_times (int, optional):
            Number of time to retry the upload in case it fails. Default is 3.
        max_upload_size (int, optional): defines the maximum size of the dataframe to be uploaded.
            Default is 2GB.
        skip_quota_warning (bool, optional): skip the quota exceeded check and force the upload.
            (The upload will still fail if the size of the dataset exceeds the remaining DB quota).
            Default is False.

    Returns:
        string: the table name normalized.

    Raises:
        ValueError: if the dataframe or table name provided are wrong or the if_exists param is not valid.

    """
    if not isinstance(dataframe, DataFrame):
        raise ValueError('Wrong dataframe. You should provide a valid DataFrame instance.')

    if isinstance(dataframe, GeoDataFrame):
        if is_reprojection_needed(dataframe):
            dataframe = reproject(dataframe)

    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    if if_exists not in IF_EXISTS_OPTIONS:
        raise ValueError('Wrong option for the `if_exists` param. You should provide: {}.'.format(
            ', '.join(IF_EXISTS_OPTIONS)))

    context_manager = ContextManager(credentials)

    if not skip_quota_warning:
        me_data = context_manager.credentials.me_data
        if me_data is not None and me_data.get('user_data'):
            n = min(SAMPLE_ROWS_NUMBER, len(dataframe))
            estimated_byte_size = len(dataframe.sample(n=n).to_csv(header=False)) * len(dataframe) \
                / n / CSV_TO_CARTO_RATIO
            remaining_byte_quota = me_data.get('user_data').get('remaining_byte_quota')

            if remaining_byte_quota is not None and estimated_byte_size > remaining_byte_quota:
                raise CartoException('DB Quota will be exceeded. '
                                     'The remaining quota is {} bytes and the dataset size is {} bytes.'.format(
                                        remaining_byte_quota, estimated_byte_size))

    gdf = GeoDataFrame(dataframe, copy=True)

    if index:
        index_name = index_label or gdf.index.name
        if index_name is not None and index_name != '':
            # Append the index as a column
            gdf[index_name] = gdf.index
        else:
            raise ValueError('Wrong index name. You should provide a valid index label.')

    if geom_col in gdf:
        set_geometry(gdf, geom_col, inplace=True, drop=True)
    elif has_geometry(dataframe):
        gdf.set_geometry(dataframe.geometry.name, inplace=True)

    if has_geometry(gdf):
        if GEOM_COLUMN_NAME in gdf and dataframe.geometry.name != GEOM_COLUMN_NAME:
            gdf.drop(columns=[GEOM_COLUMN_NAME], inplace=True)

        # Prepare geometry column for the upload
        if dataframe.geometry.name != GEOM_COLUMN_NAME:
            gdf.rename_geometry(GEOM_COLUMN_NAME, inplace=True)

    elif isinstance(dataframe, GeoDataFrame):
        log.warning('Geometry column not found in the GeoDataFrame.')

    chunk_count = math.ceil(estimate_csv_size(gdf) / max_upload_size)
    chunk_row_size = int(math.ceil(len(gdf) / chunk_count))
    chunked_gdf = [gdf[i:i + chunk_row_size] for i in range(0, gdf.shape[0], chunk_row_size)]

    for i, chunk in enumerate(chunked_gdf):
        if i > 0:
            if_exists = 'append'
        table_name = context_manager.copy_from(chunk, table_name, if_exists, cartodbfy, retry_times)

    if log_enabled:
        log.info('Success! Data uploaded to table "{}" correctly'.format(table_name))

    return table_name


def list_tables(credentials=None):
    """List all of the tables in the CARTO account.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).

    Returns:
        DataFrame: A DataFrame with all the table names for the given credentials.

    """
    context_manager = ContextManager(credentials)
    return context_manager.list_tables()


def has_table(table_name, credentials=None, schema=None):
    """Check if the table exists in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional): prefix of the table. By default, it gets the
            `current_schema()` using the credentials.

    Returns:
        bool: True if the table exists, False otherwise.

    Raises:
        ValueError: if the table name is not a valid table name.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)
    return context_manager.has_table(table_name, schema)


def delete_table(table_name, credentials=None, log_enabled=True):
    """Delete the table from the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        log_enabled (bool, optional): enable the logging mechanism. Default is True.

    Raises:
        ValueError: if the table name is not a valid table name.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)
    result = context_manager.delete_table(table_name)

    if log_enabled:
        if result:
            log.info('Success! Table "{}" removed correctly'.format(table_name))
        else:
            log.info('Table "{}" does not exist'.format(table_name))


def rename_table(table_name, new_table_name, credentials=None, if_exists='fail', log_enabled=True):
    """Rename a table in the CARTO account.

    Args:
        table_name (str): name of the table.
        new_table_name (str): new name for the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace'. Default is 'fail'.
        log_enabled (bool, optional): enable the logging mechanism. Default is True.

    Raises:
        ValueError: if the table names provided are wrong or the if_exists param is not valid.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    if not is_valid_str(new_table_name):
        raise ValueError('Wrong new table name. You should provide a valid table name.')

    IF_EXISTS_OPTIONS = ['fail', 'replace']
    if if_exists not in IF_EXISTS_OPTIONS:
        raise ValueError('Wrong option for the `if_exists` param. You should provide: {}.'.format(
            ', '.join(IF_EXISTS_OPTIONS)))

    context_manager = ContextManager(credentials)
    new_table_name = context_manager.rename_table(table_name, new_table_name, if_exists)

    if log_enabled:
        log.info('Success! Table "{0}" renamed to table "{1}" correctly'.format(table_name, new_table_name))


def copy_table(table_name, new_table_name, credentials=None, if_exists='fail', log_enabled=True, cartodbfy=True):
    """Copy a table into a new table in the CARTO account.

    Args:
        table_name (str): name of the original table.
        new_table_name (str, optional): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.
        log_enabled (bool, optional): enable the logging mechanism. Default is True.
        cartodbfy (bool, optional): convert the table to CARTO format. Default True. More info
            `here <https://carto.com/developers/sql-api/guides/creating-tables/#create-tables>`.
    Raises:
        ValueError: if the table names provided are wrong or the if_exists param is not valid.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    if not is_valid_str(new_table_name):
        raise ValueError('Wrong new table name. You should provide a valid table name.')

    if if_exists not in IF_EXISTS_OPTIONS:
        raise ValueError('Wrong option for the `if_exists` param. You should provide: {}.'.format(
            ', '.join(IF_EXISTS_OPTIONS)))

    query = 'SELECT * FROM {}'.format(table_name)

    context_manager = ContextManager(credentials)
    new_table_name = context_manager.create_table_from_query(query, new_table_name, if_exists, cartodbfy)

    if log_enabled:
        log.info('Success! Table "{0}" copied to table "{1}" correctly'.format(table_name, new_table_name))


def create_table_from_query(
        query,
        new_table_name,
        credentials=None,
        if_exists='fail',
        log_enabled=True,
        cartodbfy=True):
    """Create a new table from an SQL query in the CARTO account.

    Args:
        query (str): SQL query
        new_table_name (str): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.
        log_enabled (bool, optional): enable the logging mechanism. Default is True.
        cartodbfy (bool, optional): convert the table to CARTO format. Default True. More info
            `here <https://carto.com/developers/sql-api/guides/creating-tables/#create-tables>`.
    Raises:
        ValueError: if the query or table name provided is wrong or the if_exists param is not valid.

    """
    if not is_sql_query(query):
        raise ValueError('Wrong query. You should provide a valid SQL query.')

    if not is_valid_str(new_table_name):
        raise ValueError('Wrong new table name. You should provide a valid table name.')

    if if_exists not in IF_EXISTS_OPTIONS:
        raise ValueError('Wrong option for the `if_exists` param. You should provide: {}.'.format(
            ', '.join(IF_EXISTS_OPTIONS)))

    context_manager = ContextManager(credentials)
    new_table_name = context_manager.create_table_from_query(query, new_table_name, if_exists, cartodbfy)

    if log_enabled:
        log.info('Success! Table "{0}" created correctly'.format(new_table_name))


def describe_table(table_name, credentials=None, schema=None):
    """Describe the table in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.

    Returns:
        A dict with the `privacy`, `num_rows` and `geom_type` of the table.

    Raises:
        ValueError: if the table name is not a valid table name.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)
    query = context_manager.compute_query(table_name, schema)

    try:
        privacy = context_manager.get_privacy(table_name)
    except CartoException:
        # There is an issue with ghost tables when
        # the table is created for the first time
        log.debug('We can not retrieve the privacy from the metadata')
        privacy = ''

    return {
        'privacy': privacy,
        'num_rows': context_manager.get_num_rows(query),
        'geom_type': context_manager.get_geom_type(query)
    }


def update_privacy_table(table_name, privacy, credentials=None, log_enabled=True):
    """Update the table information in the CARTO account.

    Args:
        table_name (str): name of the table.
        privacy (str): privacy of the table: 'private', 'public', 'link'.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        log_enabled (bool, optional): enable the logging mechanism. Default is True.

    Raises:
        ValueError: if the table name is wrong or the privacy name
            is not 'private', 'public', or 'link'.

    """
    if not is_valid_str(table_name):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    valid_privacy_values = ['PRIVATE', 'PUBLIC', 'LINK']
    if privacy.upper() not in valid_privacy_values:
        raise ValueError('Wrong privacy. Valid names are {}'.format(', '.join(valid_privacy_values)))

    context_manager = ContextManager(credentials)
    context_manager.update_privacy_table(table_name, privacy)

    if log_enabled:
        log.info('Success! Table "{}" privacy updated correctly'.format(table_name))


def estimate_csv_size(gdf):
    n = min(SAMPLE_ROWS_NUMBER, len(gdf))
    columns = get_dataframe_columns_info(gdf)
    return sum([len(x) for x in
                _compute_copy_data(gdf.sample(n=n), columns)]) * len(gdf) / n
