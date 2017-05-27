"""
This file demonstrates common uses for the Python unittest module with Flask

Documentation:

* https://docs.python.org/3/library/unittest.html
* http://flask.pocoo.org/docs/latest/testing/
"""
import unittest
from app import app
from flask_sqlalchemy import SQLAlchemy


class FlaskTestCase(unittest.TestCase):
    """ This is one of potentially many TestCases """

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        # db.init_app(app)
        self.tester = app.test_client(self)
        # db.create_all()

    def test_route_home(self):
        res = self.tester.get("/")
        assert res.status_code == 200
        assert b"Se el primero" in res.data
        print('Route Home ok')

    def test_route_signup(self):
        res = self.tester.get("/signup")
        assert res.status_code == 200
        assert b"Registro" in res.data
        print('Route Signup ok')

    def test_login(self):
        post = self.tester.post('/login', data=dict(
            username='juan',
            password='123'
        ), follow_redirects=True)
        assert b'Your email or password is not valid.' in post.data
        print('Login ok')


if __name__ == '__main__':
    unittest.main()
