from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class User(db.Model):
    '''
    Table user
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password = db.Column(db.String(106), nullable=False, unique=False)
    is_active = db.Column(db.Boolean, nullable=False, unique=False)
    token = db.Column(db.String(32), nullable=False, unique=False)
    create_at = db.Column(db.DateTime, nullable=False, unique=False)

    def __init__(self):
        self.is_active = False
        self.token = str(uuid4()).replace('-', '')
        self.create_at = datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.username


class Search(db.Model):
    '''
    Table search
    '''
    __tablename__ = 'searchs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    create_at = db.Column(db.DateTime, nullable=False, unique=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
        )
    user = db.relationship(
        'users',
        backref=db.backref('searchs', lazy=True)
        )

    def __init__(self):
        self.create_at = datetime.utcnow()

    def __repr__(self):
        return '<Search %r>' % self.username


if __name__ == '__main__':
    manager.run()
