import os
import time
import glob
import pytest
import logging
import nbformat
import subprocess
from nbconvert.preprocessors import ExecutePreprocessor


logging.basicConfig(level=logging.INFO)

EXECUTE_NOTEBOOKS = []
AVOID_NOTEBOOKS = [
    'docs/examples/use_cases/building_a_dashboard.ipynb',
    'docs/examples/use_cases/combining_two_datasets.ipynb',
    'docs/examples/use_cases/geocoding_london_stations.ipynb',
    'docs/examples/use_cases/paris_remarkable_trees.ipynb',
    'docs/examples/use_cases/paris_wifi_services.ipynb',
    'docs/examples/use_cases/visualize_temperatures.ipynb',

    'docs/examples/templates/do_access_premium_data.ipynb',
    'docs/examples/templates/do_access_public_data.ipynb',
    'docs/examples/templates/do_data_discovery.ipynb',
    'docs/examples/templates/do_data_enrichment.ipynb',
    'docs/examples/templates/do_dataset_notebook_template.ipynb',
    'docs/examples/templates/do_geography_notebook_template.ipynb',

    'docs/examples/data_observatory/download_dataset.ipynb',
    'docs/examples/data_management/change_carto_table_privacy.ipynb',
    'docs/examples/publish_and_share/publish_visualization_layout.ipynb',
    'docs/examples/publish_and_share/publish_visualization_private_table.ipynb',
    'docs/examples/publish_and_share/publish_visualization_public_table.ipynb'
]

OVERWRITE = os.environ.get('OVERWRITE', 'true').lower() == 'true'
TIMEOUT = int(os.environ.get('TIMEOUT', 600))
KERNEL = os.environ.get('KERNEL', 'python3').lower()
SCOPE = os.environ.get('SCOPE', 'all').lower()

with open('tests/notebooks/creds.json', 'r') as creds_file:
    CREDS_FILE = creds_file.read()


def find_notebooks():
    notebooks = []

    if EXECUTE_NOTEBOOKS:
        notebooks = list(set(EXECUTE_NOTEBOOKS) - set(AVOID_NOTEBOOKS))
    else:
        if SCOPE in ['all', 'guides']:
            notebooks += glob.glob('docs/guides/**/*.ipynb', recursive=True)
        if SCOPE in ['all', 'examples']:
            notebooks += glob.glob('docs/examples/**/*.ipynb', recursive=True)
        notebooks = list(set(notebooks) - set(AVOID_NOTEBOOKS))

    notebooks.sort()
    return notebooks


class TestNotebooks:
    def teardown(self):
        time.sleep(0.1)

    def custom_setup(self, path):
        with open('{}/creds.json'.format(path), 'w') as creds_file:
            creds_file.write(CREDS_FILE)

    def custom_teardown(self, path):
        os.remove('{}/creds.json'.format(path))

    @pytest.mark.parametrize('notebook_filename', find_notebooks())
    def test_docs(self, notebook_filename):
        try:
            path = os.path.dirname(notebook_filename)

            self.custom_setup(path)
            self.execute_notebook(notebook_filename, path)
        finally:
            self.custom_teardown(path)

    def execute_notebook(self, notebook_filename, path):
        with open(notebook_filename) as f:
            logging.info('\nExecuting notebook: %s', notebook_filename)

            nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=TIMEOUT, kernel_name=KERNEL, allow_errors=OVERWRITE,
                                     store_widget_state=OVERWRITE)
            ep.preprocess(nb, {'metadata': {'path': path}})

            if OVERWRITE:
                logging.info('Overwriting notebook: %s', notebook_filename)
                with open(notebook_filename, 'w') as fwrite:
                    nbformat.write(nb, fwrite)

                logging.info('Trusting notebook: %s', notebook_filename)
                p_jupyter = subprocess.Popen('jupyter trust {}'.format(notebook_filename), shell=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, stderr_jupyter = p_jupyter.communicate()

                if len(stderr_jupyter) > 0:
                    raise RuntimeError('Error trusting the notebook ({}): {}'.format(notebook_filename, stderr_jupyter))
