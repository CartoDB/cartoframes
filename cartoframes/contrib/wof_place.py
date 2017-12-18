import requests
import json
from shapely.geometry import shape
from cartoframes import utils

placetype_hierarchy = {
    "country": "region",
    "region": "county",
    "county": "locality",
    "locality": "neighbourhood"
  }

class Place:
    '''
    A place from the Who's On First gazateer.

    Attributes:
        wof_id = WOF unique identifier as an integer
        place = The place name as a string
        placetype = WOF placetype as a string (eg. region, county, locality, neighbourhood...)
        geometry = Shapely representation of the place geometry (eg. polygon, point...)
        bbox = WOF bounding box of geometry as list of floats
    '''
    def __init__(self, place, mapzen_key, wof_id=None, placetype='region'):
        self.mapzen_key = mapzen_key
        if wof_id == None:
            _placesSearchURL = 'https://places.mapzen.com/v1/?method=mapzen.places.search' \
                              '&api_key={api_key}&names={names}&id={wof_id}' \
                              '&placetype={placetype}&per_page=500' \
                              '&extras=mz:uri'
            self.results = requests.get(_placesSearchURL.format(names=place,
                                                                wof_id=wof_id,
                                                                placetype=placetype,
                                                                api_key=mapzen_key)).json()['places']
            self.wof_id = self.results[0]['wof:id']
            self.placetype = self.results[0]['wof:placetype']
            self.geometry = shape(requests.get(self.results[0]['mz:uri']).json()['geometry'])
            self.bbox = requests.get(self.results[0]['mz:uri']).json()['bbox']

        elif wof_id != None:
            _getInfoURL = 'https://places.mapzen.com/v1/?method=mapzen.places.getInfo'\
                        '&api_key={api_key}&id={wof_id}&extras=mz:uri'

            self.results = requests.get(_getInfoURL.format(wof_id=wof_id,
                                                    api_key=mapzen_key)).json()['place']
            self.wof_id = self.results['wof:id']
            self.placetype = self.results['wof:placetype']
            self.geometry = shape(requests.get(self.results['mz:uri']).json()['geometry'])
            self.bbox = requests.get(self.results['mz:uri']).json()['bbox']

        self.place = place
        self._descendants = utils.normalize_colnames(self._get_descendants()[1],warn=False)
        self._descendants_info = self._get_descendants()[0]

    def _get_descendants(self):
        getDescendantsURL = 'https://places.mapzen.com/v1/?method=mapzen.places.getDescendants'\
                            '&api_key={api_key}&id={id}&placetype={placetype}&extras=wof:placetype'
        next_level = placetype_hierarchy.get(self.placetype, "")
        resp = requests.get(getDescendantsURL.format(id=self.wof_id, placetype=next_level, api_key=self.mapzen_key))
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
