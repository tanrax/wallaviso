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
from utils import UtilSearch
from flask import render_template
from models import db, Search, User, OldSearch
from flask_mail import Mail, Message


mail = Mail(app)
manager = Manager(app)

@manager.command
def notify():
    util_search = UtilSearch()
    searchs = Search.query.all()
    for search in searchs:
        # Get data
        results = util_search.get(search.name)
        my_olds = OldSearch.query.filter_by(search_id=search.id)
        # Check new items
        for item in results:
            notify = True
            for old in my_olds:
                if item['itemId'] == old.item_id:
                    notify = False
            if notify:
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
                # Add id in old_searchs table
                my_new_old = OldSearch()
                my_new_old.item_id = int(item['itemId'])
                my_new_old.search_id = search.id
                db.session.add(my_new_old)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()


if __name__ == "__main__":
    manager.run()
