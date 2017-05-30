from flask_script import Manager

from app import app
from models import db, Search
import json
from urllib3 import PoolManager
import urllib.parse


manager = Manager(app)
http = PoolManager()


@manager.command
def notify():
    searchs = Search.query.all()
    for search in searchs:
        # Get data
        url_api = 'http://es.wallapop.com/rest/items?minPrice=&maxPrice=&dist=0_&order=creationDate-des&lat=41.398077&lng=2.170432&kws=' + urllib.parse.quote(search.name, safe='')
        results = http.request('GET', url_api)
        results = json.loads(
            results.data.decode('utf-8')
        )['items'][:10]
        #results = results[::-1]
        # Check new items
        if results[0]['itemId'] != search.last_id:
            validate = True
            for item in results:
                if validate:
                    if item['itemId'] != search.last_id:
                        # Send email
                        print(item['itemId'])
                        print(item['title'])
                    else:
                        validate = False
            # Update last id
            my_user_search = Search.query.filter_by(id=search.id).first()
            my_user_search.last_id = results[0]['itemId']
            db.session.add(my_user_search)
            try:
                db.session.commit()
            except:
                db.session.rollback()





if __name__ == "__main__":
    manager.run()
