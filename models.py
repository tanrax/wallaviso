from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')
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
    rol_id = db.Column(
        db.Integer,
        db.ForeignKey('rols.id'),
        nullable=False,
        default=1
        )
    create_at = db.Column(db.DateTime, nullable=False, unique=False)

    # Relations

    rol = db.relationship(
        'Rol',
        backref=db.backref('User')
        )

    def __init__(self):
        self.is_active = False
        self.token = str(uuid4()).replace('-', '')
        self.rol_id = 1
        self.create_at = datetime.now()

    def __repr__(self):
        return '<User %r>' % self.username


class Rol(db.Model):
    '''
    Table Rol
    1 - Free (Gratuita)
    2 - Premium (Premium)
    '''
    __tablename__ = 'rols'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=False)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Rol %r>' % self.name


class Search(db.Model):
    '''
    Table search
    '''
    __tablename__ = 'searchs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    lat = db.Column(db.Float, nullable=False, unique=False, default=0)
    lng = db.Column(db.Float, nullable=False, unique=False, default=0)
    max_price = db.Column(db.Float, nullable=False, unique=False, default=0)
    min_price = db.Column(db.Float, nullable=False, unique=False, default=0)
    alert_expiration = db.Column(db.Boolean, nullable=False, default=False)
    distance = db.Column(
        db.String(7),
        nullable=False,
        unique=False,
        default='0_'
        )
    token = db.Column(db.String(32), nullable=False, unique=False)
    update_at = db.Column(db.DateTime, nullable=False, unique=False)
    create_at = db.Column(db.DateTime, nullable=False, unique=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
        )
    user = db.relationship(
        'User',
        backref=db.backref('Search', cascade="all, delete-orphan")
        )

    def __init__(self):
        self.token = str(uuid4()).replace('-', '')
        self.update_at = datetime.now()
        self.create_at = datetime.now()

    def __repr__(self):
        return '<Search %r>' % self.name


@manager.command
def init_data():
    # Reload tables
    db.drop_all()
    db.create_all()

    my_rol_1 = Rol()
    my_rol_1.name = 'Gratuita'
    db.session.add(my_rol_1)

    my_rol_2 = Rol()
    my_rol_2.name = 'Premium'
    db.session.add(my_rol_2)

    db.session.commit()


if __name__ == '__main__':
    manager.run()

