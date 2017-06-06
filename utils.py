import json
from urllib3 import PoolManager
import urllib.parse


class UtilSearch():

    def get(self, name, lat=41.398077, lng=2.170432, dist='0_'):
        url_api = 'http://es.wallapop.com/rest/items?minPrice=&maxPrice=&dist={dist}&order=creationDate-des&lat={lat}&lng={lng}&kws={kws}'.format(
            kws=urllib.parse.quote(name, safe=''),
            lat=lat,
            lng=lng,
            dist=dist
        )
        results = self.http.request('GET', url_api)
        results = json.loads(
            results.data.decode('utf-8')
        )
        return results['items']

    def __init__(self):
        self.http = PoolManager()
