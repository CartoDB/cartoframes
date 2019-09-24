import datetime
import pytz

from ..enrichment import fake_auth
from google.cloud import bigquery

# TODO: decorator to authenticate


class BigQueryClient(object):

    def __init__(self, credentials):
        token = fake_auth.auth(credentials)

        self.credentials = credentials
        self.client = bigquery.Client().from_service_account_json(token)  # Change auth method when token received

    def upload_dataframe(self, dataframe, schema, tablename, project, dataset, ttl_days=None):
        dataset_ref = self.client.dataset(dataset, project=project)
        table_ref = dataset_ref.table(tablename)

        schema_wrapped = [bigquery.SchemaField(column, dtype) for column, dtype in schema.items()]

        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema_wrapped

        job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
        job.result()

        if ttl_days:
            table = self.client.get_table(table_ref)
            expiration = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=ttl_days)
            table.expires = expiration
            self.client.update_table(table, ["expires"])

    def query(self, query, **kwargs):
        response = self.client.query(query, **kwargs)

        return response

    def delete_table(self, tablename, project, dataset):
        dataset_ref = self.client.dataset(dataset, project=project)
        table_ref = dataset_ref.table(tablename)
        self.client.delete_table(table_ref)
