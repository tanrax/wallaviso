from os import environ
from flask import Flask, render_template
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# Flask
app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Email
app.config['MAIL_SERVER'] = environ.get('MAIL_SERVER', 'localhost')
app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME', None)
app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD', None)
app.config['MAIL_PORT'] = environ.get('MAIL_PORT', 25)

mail = Mail(app)

manager = Manager(app)

@manager.command
def send_news():
    # Get all users
    my_users = User.query.all()

    for user in my_users:
        msg = Message(
            'Noticia importante',
            sender='no-reply@wallaviso.com',
            recipients=[user.email]
        )
        msg.body = render_template(
            'emails/news.txt',
            username=user.username
        )
        msg.html = render_template(
            'emails/news.html',
            username=user.username
        )
        try:
            mail.send(msg)
        except:
            pass

if __name__ == '__main__':
    manager.run()

