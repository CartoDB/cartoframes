"""
An experiment to build a carto interface into pandas dataframes
"""
from pandas import DataFrame


class CartoDF(DataFrame):
    """
        cartodataframe (subclasses pandas dataframe)
    """
    def __init__(self, username=None, api_key=None, *args, **kw):
        super(CartoDF, self).__init__(*args, **kw)
        if api_key:
            self.api_key = api_key
        self.cdb_username = username
        self.map_id = None

    def get_api_key(self):
        """
            Return CARTO API key
        """
        print self.api_key

    def set_map_id(self, map_id):
        """
            Return map id of the registered map/dataset
        """
        self.map_id = map_id

    def get_table(self, tablename):
        """
            Retrieve a table from CARTO and turn it into a dataframe
        """
        import pandas as pd
        api_format = ('https://{username}.carto.com/api/v2/sql?q='
                      'SELECT%20*%20FROM%20{tablename}&format=csv')
        request = api_format.format(
            username=self.cdb_username,
            tablename=tablename)
        return pd.read_csv(request)

    # upload interface
    def to_carto(self, dataframe, tablename=None):
        """
            Send a dataframe to CARTO and create a new table
        """
        import requests
        import json
        if tablename is None:
            tablename = 'testing_upload'
        tablename = ('%s.csv' % tablename)
        dataframe.to_csv(tablename)
        files = {'file': open(tablename, 'r')}
        post_template = ('https://{username}.carto.com/api/v1/imports/'
                         '?api_key={api_key}')
        try:
            resp = requests.post(post_template.format(
                username=self.cdb_username,
                api_key=self.api_key), files=files)
        except Exception, err:
            print "Error: %s" % err
        print resp.text
        if json.loads(resp.content)['success']:
            print 'File successfully uploaded'
        else:
            print 'File failed to upload'
        return json.loads(resp.content)['success']

    def sync(self):
        """
            Update CARTO table registered with this dataframe to have the new
            values, columns, etc.
        """
        # sync with an existing carto table
        pass

    def map(self, static=True):
        """
            Retrieve a static or interactive map from the registered dataset
        """
        import json
        # generate carto map
        params = {
            'username': json.loads(self.meta)['username'],
            'api_key': json.loads(self.meta)['api_key']
            }

        if static:
            # use static maps api
            pass
        else:
            # return iframe code or full-screen embed link?
            pass
        return None
