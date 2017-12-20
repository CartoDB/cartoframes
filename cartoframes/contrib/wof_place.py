import requests
import json
from shapely.geometry import shape
import pandas as pd
from cartoframes import utils
import utils as contributils

placetype_hierarchy = {
    "country": "region",
    "region": "county",
    "county": "locality",
    "locality": "neighbourhood"
  }

_placesSearchURL = 'https://places.mapzen.com/v1/?method=mapzen.places.search' \
                  '&api_key={api_key}&names={names}&id={wof_id}' \
                  '&placetype={placetype}&per_page=500' \
                  '&extras=mz:uri,wof:hierarchy'

_getInfoURL = 'https://places.mapzen.com/v1/?method=mapzen.places.getInfo'\
            '&api_key={api_key}&id={wof_id}&extras=mz:uri,wof:hierarchy'

_getDescendantsURL = 'https://places.mapzen.com/v1/?method=mapzen.places.getDescendants'\
                    '&api_key={api_key}&id={id}&placetype={placetype}&extras=wof:placetype,mz:uri'

class Place:
    '''
    A place from the Who's On First gazateer.

    Args:
        place (str): Place name used to search across all WOF name fields.
        mapzen_key (str): A valid Mapzen API key
        wof_id (int, optional): WOF unique identifier to retrieve.
        placetype (str, optional): WOF placetype, defaults to 'region'

    Attributes:
        wof_id = The WOF unique identifier as an integer
        place = The place name as a string
        placetype = WOF placetype as a string (eg. region, county, locality, neighbourhood...)
        geometry = Shapely representation of the place geometry (eg. polygon, point...)
        bbox = WOF bounding box of geometry as list of floats
        hierarchy = WOF ancestors of a place as a list of dictionaries
        next_level = WOF placetype of the next immediate descendant, string or None
        mzuri = The WOF URL to the geojson as a string
    '''
    def __init__(self, place, mapzen_key, wof_id=None, placetype='region'):

        # todo: try to save mapzen key the same way as cartocontext Credentials
        self.mapzen_key = mapzen_key

        # Search by "place" in all WOF name fields, assume first return is "correct"
        # Could be made better... to allow for place discovery and selection. Need to figure out
        # pagination in the API (to get all descendants, to get all matches, etc...)

        if wof_id == None:
            self.results = requests.get(_placesSearchURL.format(names=place,
                                                                wof_id=wof_id,
                                                                placetype=placetype,
                                                                api_key=mapzen_key)).json()['places']
            first_result = self.results[0]
            self.wof_id = first_result['wof:id']
            self.placetype = first_result['wof:placetype']
            self.geometry = shape(requests.get(first_result['mz:uri']).json()['geometry'])
            self.bbox = requests.get(first_result['mz:uri']).json()['bbox']
            self.parents = first_result['wof:hierarchy']
            self.mzuri = first_result['mz:uri']

        elif wof_id != None:
            self.results = requests.get(_getInfoURL.format(wof_id=wof_id,
                                                    api_key=mapzen_key)).json()['place']
            self.wof_id = self.results['wof:id']
            self.placetype = self.results['wof:placetype']
            self.geometry = shape(requests.get(self.results['mz:uri']).json()['geometry'])
            self.bbox = requests.get(self.results['mz:uri']).json()['bbox']
            self.parents = self.results['wof:hierarchy']
            self.mzuri = self.results['mz:uri']

        self.place = place
        self._descendants = utils.normalize_colnames(self._get_descendants()[1],warn=False)
        self._descendants_info = self._get_descendants()[0]
        self.next_level = placetype_hierarchy.get(self.placetype, "")


    def _get_descendants(self):
        next_level = placetype_hierarchy.get(self.placetype, "")
        resp = requests.get(_getDescendantsURL.format(id=self.wof_id, placetype=next_level, api_key=self.mapzen_key))
        descendant_names = []
        for descendant in resp.json()['places']:
            descendant_names.append(descendant['wof:name'])
        return resp.json(), descendant_names

    def __dir__(self):
        # show the available
        normed_descendants = utils.normalize_colnames(self._descendants,warn=False)
        return normed_descendants

    def __getattr__(self,method_name):
        next_level = placetype_hierarchy.get(self.placetype, "")
        if method_name in self._descendants:
            name_change_dict = dict(zip(self._descendants, self._get_descendants()[1]))
            original_name = name_change_dict.get(method_name,'')
            print("Getting the WOF place for " + original_name)
            next_wof_id = next((item for item in self._descendants_info['places'] if item["wof:name"] == original_name))['wof:id']
            return Place(method_name, self.mapzen_key, wof_id=next_wof_id, placetype=next_level)
        else:
            raise AttributeError('No such attribute: {method_name}'.format(method_name=method_name))

    def get_descendants(self, placetype):
        '''
        Returns all the descendants of this WOF place
        at the requested placetype level as a cartoframes-ready DataFrame
        with geometry and select attributes
        '''
        descendants_csv_url = _getDescendantsURL.format(id=self.wof_id,
                                                        placetype=placetype,
                                                        api_key=self.mapzen_key) \
                                                        +'&format=csv'
        descendants_df = pd.read_csv(descendants_csv_url)
        descendants_df = contributils.df_add_geometries(descendants_df)
        return descendants_df

    def explore_data(self):
        # returns dataframe of available CARTO Data Observatory measures for this place
        # using same method as data_discovery
        return None

    def get_data(self, measure, placetype_descendants='localities', ):
        # returns a measure
        return None
