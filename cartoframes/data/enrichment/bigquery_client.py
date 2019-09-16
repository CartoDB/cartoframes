from . import fake_auth

from google.cloud import bigquery

_WORKING_PROJECT = 'cartodb-on-gcp-datascience'
_TEMP_DATASET_ENRICHMENT = 'enrichment_temp'

# TODO: decorator to authenticate


class BigQueryClient(object):

    def __init__(self, credentials):
        token = fake_auth.auth(credentials)

        self.credentials = credentials
        self.client = bigquery.Client().from_service_account_json(token)  # Change auth method when token received

    def upload_dataframe(self, dataframe, data_id_column, data_geom_column, tablename):
        dataset_ref = self.client.dataset(_TEMP_DATASET_ENRICHMENT, project=_WORKING_PROJECT)
        table_ref = dataset_ref.table(tablename)

        job_config = bigquery.LoadJobConfig()
        job_config.schema = [
            bigquery.SchemaField(data_id_column, 'INTEGER'),
            bigquery.SchemaField(data_geom_column, "GEOGRAPHY"),
        ]

        job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
        job.result()

    def query(self, query, **kwargs):
        response = self.client.query(query, **kwargs)

        return response

    def delete_table(self, tablename):
        dataset_ref = self.client.dataset(_TEMP_DATASET_ENRICHMENT, project=_WORKING_PROJECT)
        table_ref = dataset_ref.table(tablename)
        self.client.delete_table(table_ref)
