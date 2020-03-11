import uuid
import pandas
from geopandas import GeoDataFrame
from carto.do_dataset import DODataset

from ...observatory import Variable
from ....auth import get_default_credentials
from ....exceptions import EnrichmentError
from ....utils.geom_utils import set_geometry, has_geometry
from ....utils.utils import timelogger

_ENRICHMENT_ID = '__enrichment_id'
_GEOM_COLUMN = '__geom_column'
_TTL_IN_SECONDS = 3600

AGGREGATION_DEFAULT = 'default'


class EnrichmentService(object):
    """Base class for the Enrichment utility with commons auxiliary methods"""

    def __init__(self, credentials=None):
        self.auth_client = _create_auth_client(credentials or get_default_credentials())

    @timelogger
    def _enrich(self, geom_type, dataframe, variables, geom_col=None, filters=None, aggregation=AGGREGATION_DEFAULT):
        filters = filters or {}
        variable_ids = self._prepare_variables(variables)
        geodataframe = self._prepare_data(dataframe, geom_col)
        temp_table_name = self._get_temp_table_name()
        uploaded_dataset = self._upload_data(temp_table_name, geodataframe)
        enriched_dataframe = self._execute_enrichment(uploaded_dataset,
                                                      temp_table_name,
                                                      geom_type,
                                                      variable_ids,
                                                      filters,
                                                      aggregation)
        return self._merge(geodataframe, enriched_dataframe)

    def _prepare_variables(self, variables):
        _variables = []

        if isinstance(variables, list):
            _variables = [v.id if isinstance(v, Variable) else v for v in variables]
        elif isinstance(variables, str):
            _variables = [variables]
        elif isinstance(variables, Variable):
            _variables = [variables.id]

        return _variables

    @timelogger
    def _prepare_data(self, dataframe, geom_col):
        geodataframe = GeoDataFrame(dataframe, copy=True)

        if geom_col in geodataframe:
            set_geometry(geodataframe, geom_col, inplace=True)
        elif has_geometry(dataframe):
            geodataframe.set_geometry(dataframe.geometry.name, inplace=True)
        else:
            raise ValueError('No valid geometry found. Please provide an input source with ' +
                             'a valid geometry or specify the "geom_col" param with a geometry column.')

        # Add extra columns for the enrichment
        geodataframe[_ENRICHMENT_ID] = range(geodataframe.shape[0])
        geodataframe[_GEOM_COLUMN] = geodataframe.geometry

        return geodataframe

    @timelogger
    def _upload_data(self, temp_table_name, geodataframe):
        reduced_geodataframe = geodataframe[[_ENRICHMENT_ID, _GEOM_COLUMN]]

        dataset = DODataset(auth_client=self.auth_client).name(temp_table_name) \
            .column(_ENRICHMENT_ID, 'INT64') \
            .column(_GEOM_COLUMN, 'GEOMETRY') \
            .ttl_seconds(_TTL_IN_SECONDS)
        dataset.create()

        status = dataset.upload_dataframe(reduced_geodataframe, _GEOM_COLUMN)

        if status not in ['success']:
            raise EnrichmentError('Couldn\'t upload the dataframe to be enriched. The job hasn\'t finished successfuly')

        return dataset

    @timelogger
    def _execute_enrichment(self, dataset, temp_table_name, geom_type, variables, filters, aggregation):
        output_name = '{}_result'.format(temp_table_name)
        status = dataset.enrichment(geom_type=geom_type,
                                    variables=variables,
                                    filters=filters,
                                    aggregation=aggregation,
                                    output_name=output_name)

        if status not in ['success']:
            raise EnrichmentError('Couldn\'t enrich the dataframe. The job hasn\'t finished successfuly')

        result = DODataset(auth_client=self.auth_client).name(output_name).download_stream()
        enriched_dataframe = pandas.read_csv(result)

        return enriched_dataframe

    def _merge(self, geodataframe, enriched_dataframe):
        result = geodataframe.merge(enriched_dataframe, on=_ENRICHMENT_ID, how='left')
        result.drop(_ENRICHMENT_ID, axis=1, inplace=True)
        result.drop(_GEOM_COLUMN, axis=1, inplace=True)

        return result

    def _get_temp_table_name(self):
        id_tablename = uuid.uuid4().hex
        return 'temp_{id}'.format(id=id_tablename)


def _create_auth_client(credentials):
    return credentials.get_api_key_auth_client()
