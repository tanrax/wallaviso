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
from datetime import datetime, timedelta
from uuid import uuid4


mail = Mail(app)
manager = Manager(app)


@manager.command
def notify():
    '''
    Check news items and send email
    '''
    util_search = UtilSearch()
    searchs = Search.query.all()
    for search in searchs:
        # Get data
        if search.lat != 0 and search.lng != 0:
            results = util_search.get(
                search.name,
                search.lat,
                search.lng,
                search.distance
                )
        else:
            results = util_search.get(name=search.name, dist=search.distance)
        my_olds = OldSearch.query.filter_by(search_id=search.id)
        # Check new items
        for item in results:
            notify = True
            for old in my_olds:
                if item['itemId'] == old.item_id:
                    notify = False
            if notify:
                # Send email
                msg = Message(
                    '¡Nuevo aviso!',
                    sender='no-reply@' + getenv('DOMAIN'),
                    recipients=[search.user.email]
                    )
                msg.body = render_template(
                    'emails/notify.txt', domain=getenv('DOMAIN'),
                    search=search.name,
                    item=item,
                    username=search.user.username
                )
                msg.html = render_template(
                    'emails/notify.html',
                    domain=getenv('DOMAIN'),
                    search=search.name,
                    item=item,
                    username=search.user.username
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


@manager.command
def update_expiration():
    '''
    Check if the search has more than two weeks.
    Then send an email to update it.
    '''
    # Check olds
    current_time = datetime.utcnow()
    two_weeks_ago = current_time - timedelta(weeks=2)
    searchs = Search.query.filter(
        Search.update_at < two_weeks_ago
        ).filter_by(alert_expiration=False).all()
    for search in searchs:
        # Update token
        search.token = str(uuid4()).replace('-', '')
        search.alert_expiration = True
        db.session.add(search)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        # Send email
        msg = Message(
            'Mantener búsqueda',
            sender='no-reply@' + getenv('DOMAIN'),
            recipients=[search.user.email]
            )
        msg.body = render_template(
            'emails/expiration.txt', domain=getenv('DOMAIN'),
            search=search
        )
        msg.html = render_template(
            'emails/expiration.html',
            domain=getenv('DOMAIN'),
            search=search
        )
        try:
            mail.send(msg)
        except:
            pass


@manager.command
def remove_expiration():
    '''
    Remove if the search has more than two weeks and two days.
    '''
    # Check olds
    current_time = datetime.utcnow()
    two_weeks_ago = current_time - timedelta(weeks=2, days=2)
    searchs = Search.query.filter(
        Search.update_at < two_weeks_ago
        ).filter_by(alert_expiration=True).all()
    for search in searchs:
        db.session.delete(search)
        try:
            db.session.commit()
        except:
            db.session.rollback()


if __name__ == "__main__":
    manager.run()
