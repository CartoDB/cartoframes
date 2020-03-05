"""Functions to interact with the Google BigQuery platform"""

import os
import json


def get_project():
    return os.environ.get('GOOGLE_CLOUD_PROJECT')


def get_token():
    path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if path:
        with open(path) as f:
            adc = json.load(f)
            if adc:
                resp = adc.get('token_response')
                if resp:
                    return resp.get('access_token')


def create_tileset(data, name=None, project=None, credentials=None, index_col='geoid', geom_col='geom'):
    raise NotImplementedError()
