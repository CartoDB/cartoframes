from pandas import DataFrame


class CartoDF(DataFrame):
    def __init__(self, username=None, api_key=None, *args, **kw):
        super(CartoDF, self).__init__(*args, **kw)
        if api_key:
            self.api_key = api_key
        self.cdb_username = username
        self.map_id = None

    def get_api_key(self):
        print self.api_key

    def set_map_id(self, map_id):
        self.map_id = map_id

    def get_table(self, tablename):
        import pandas as pd
        api_format = ('https://{username}.carto.com/api/v2/sql?q='
                      'SELECT%20*%20FROM%20{tablename}&format=csv')
        request = api_format.format(
            username=self.cdb_username,
            tablename=tablename)
        return pd.read_csv(request)

    # upload interface
    def to_carto(self, df, tablename=None):
        import requests
        import json
        if tablename is None:
            tablename = 'testing_upload'
        tablename = ('%s.csv' % tablename)
        df.to_csv(tablename)
        files = {'file': open(tablename)}
        post_template = ('https://{username}.carto.com/api/v1/imports/'
                         '?api_key={api_key}')
        try:
            r = requests.post(post_template.format(
                    username=self.cdb_username,
                    api_key=self.api_key), files=files)
        except Exception, err:
            print("Error: %s" % err)
        if json.loads(r.content)['success']:
            print('File successfully uploaded')
        else:
            print('File failed to upload')
        return json.loads(r.content)['success']

    def sync(self):
        # sync with an existing carto table
        pass

    def map(self, static=True):
        # generate carto map
        if static:
            # use static maps api
            pass
        else:
            # return iframe code or full-screen embed link?
            pass
        pass
