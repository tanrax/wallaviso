"""
This file demonstrates common uses for the Python unittest module with Flask

Documentation:
* https://docs.python.org/3/library/unittest.html
* http://flask.pocoo.org/docs/latest/testing/
"""
import unittest
from app import app, db
from models import User


class FlaskTestCase(unittest.TestCase):
    """ This is one of potentially many TestCases """

    def setUp(self):
        self.db_name = 'test.sqlite'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_name
        self.app = app.test_client(app)
        db.create_all()

    def tearDown(self):
        my_user = User.query.filter_by(email='test@test.com')
        db.session.delete(my_user)
        db.session.commit()
        pass

    def test_route_home(self):
        res = self.app.get('/')
        assert res.status_code == 200
        assert b"Se el primero" in res.data
        print('Route Home ok')

    def test_route_signup(self):
        res = self.app.get("/signup")
        assert res.status_code == 200
        assert b"Registro" in res.data
        print('Route Signup ok')

    def test_signup(self):
        post = self.app.post('/signup', data=dict(
            username='',
            email='',
            password='',
            password_confirm=''
        ), follow_redirects=True)
        assert b'Campo obligatorio' in post.data

        post = self.app.post('/signup', data=dict(
            username='te',
            email='',
            password='',
            password_confirm=''
        ), follow_redirects=True)
        assert b'Debe tener entre 5 y 30' in post.data

        post = self.app.post('/signup', data=dict(
            username='qwertyuiopasdfghjklzxcvbnmqwertyu',
            email='',
            password='',
            password_confirm=''
        ), follow_redirects=True)
        assert b'Debe tener entre 5 y 30' in post.data

        post = self.app.post('/signup', data=dict(
            username='user_test',
            email='test@test',
            password='',
            password_confirm=''
        ), follow_redirects=True)
        assert b'No tiene un formato' in post.data

        post = self.app.post('/signup', data=dict(
            username='user_test',
            email='test@test',
            password='',
            password_confirm=''
        ), follow_redirects=True)
        assert b'Campo obligatorio' in post.data

        post = self.app.post('/signup', data=dict(
            username='user_test',
            email='test@test.com',
            password='123',
            password_confirm=''
        ), follow_redirects=True)
        assert b'as no coinciden' in post.data

        post = self.app.post('/signup', data=dict(
            username='user_test',
            email='test@test.test',
            password='123',
            password_confirm='123'
        ), follow_redirects=True)
        assert b'Te hemos enviado un email' in post.data
        print(User.query.all())

        post = self.app.post('/signup', data=dict(
            username='user_test',
            email='test@test.test',
            password='123',
            password_confirm='123'
        ), follow_redirects=True)
        assert b'El email ya esta siendo utilizado' in post.data

        print('Signup ok')


    def test_login(self):
        db.create_all()
        post = self.app.post('/login', data=dict(
            email='test@test.test',
            password='123'
        ), follow_redirects=True)
        assert b'Your email or password is not valid.' in post.data
        print('Login ok')


if __name__ == '__main__':
    unittest.main()

