import fcntl, sys
pid_file = 'tasks.pid'
fp = open(pid_file, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    # another instance is running
    sys.exit(0)

from flask_script import Manager

from os import getenv
from app import app
from flask import render_template
from models import db, Search, User
import json
from flask_mail import Mail, Message
from urllib3 import PoolManager
import urllib.parse


mail = Mail(app)
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
        # Check new items
        if results[0]['itemId'] != search.last_id:
            validate = True
            for item in results:
                if validate:
                    if item['itemId'] != search.last_id:
                        # Send email
                        my_user = User.query.filter_by(
                            id=search.user_id
                        ).first()
                        msg = Message(
                            '¡Nuevo aviso!',
                            sender='no-repy@' + getenv('DOMAIN'),
                            recipients=[my_user.email]
                            )
                        msg.body = render_template(
                            'emails/notify.txt', domain=getenv('DOMAIN'),
                            search=search.name,
                            item=item,
                            username=my_user.username
                        )
                        msg.html = render_template(
                            'emails/notify.html',
                            domain=getenv('DOMAIN'),
                            search=search.name,
                            item=item,
                            username=my_user.username
                        )
                        mail.send(msg)
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
