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
    'docs/examples/data_observatory/download_dataset.ipynb',
    'docs/examples/data_management/change_carto_table_privacy.ipynb',
    'docs/examples/publish_and_share/publish_visualization_layout.ipynb',
    'docs/examples/publish_and_share/publish_visualization_private_table.ipynb',
    'docs/examples/publish_and_share/publish_visualization_public_table.ipynb',
    'docs/examples/_debug/testing_polygons_features.ipynb',
    'docs/examples/_debug/enrichment_big_polygons.ipynb',
]

OVERWRITE = os.environ.get('OVERWRITE', 'true').lower() == 'true'
TIMEOUT = int(os.environ.get('TIMEOUT', 600))
KERNEL = os.environ.get('KERNEL', 'python3').lower()
SCOPE = os.environ.get('SCOPE', 'all').lower()

with open('tests/notebooks/creds.json', 'r') as creds_file:
    CREDS_FILE = creds_file.read()


def find_notebooks():
    if EXECUTE_NOTEBOOKS:
        return list(set(EXECUTE_NOTEBOOKS) - set(AVOID_NOTEBOOKS))
    else:
        notebooks = []
        if SCOPE in ['all', 'guides']:
            notebooks += glob.glob('docs/guides/**/*.ipynb', recursive=True)
        if SCOPE in ['all', 'examples']:
            notebooks += glob.glob('docs/examples/**/*.ipynb', recursive=True)
        return list(set(notebooks) - set(AVOID_NOTEBOOKS))


class TestNotebooks:
    def teardown(self):
        time.sleep(10)

    def custom_setup(self, path):
        with open('{}/creds.json'.format(path), 'w') as creds_file:
            creds_file.write(CREDS_FILE)

    def custom_teardown(self, path):
        os.remove('{}/creds.json'.format(path))

    @pytest.mark.parametrize('notebook_filename', find_notebooks())
    def test_docs(self, notebook_filename):
        try:
            path = '/'.join(notebook_filename.split('/')[:-1])

            self.custom_setup(path)
            self.execute_notebook(notebook_filename, path)
        finally:
            self.custom_teardown(path)

    def execute_notebook(self, notebook_filename, path):
        with open(notebook_filename) as f:
            logging.info('Executing notebook: %s', notebook_filename)

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
