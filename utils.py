import requests

class UtilSearch():

    def get(self, name, lat=41.398077, lng=2.170432, dist='0_', max_price=0):
        url_api = ('http://es.wallapop.com/rest/items?minPrice='
                   '&maxPrice={max_price}&dist={dist}&order=creationDate-des'
                   '&lat={lat}&lng={lng}&kws={kws}'
                  ).format(
                        kws=name,
                        lat=lat,
                        lng=lng,
                        dist=dist,
                        max_price=max_price
                    )
        results = requests.get(url_api).json()
        return results['items']
