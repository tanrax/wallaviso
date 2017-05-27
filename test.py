"""
This file demonstrates common uses for the Python unittest module with Flask

Documentation:

* https://docs.python.org/3/library/unittest.html
* http://flask.pocoo.org/docs/latest/testing/
"""
import unittest
from app import app


class FlaskTestCase(unittest.TestCase):
    """ This is one of potentially many TestCases """

    def setUp(self):
        self.tester = app.test_client(self)

    def test_route_home(self):
        res = self.tester.get("/")
        assert res.status_code == 200
        assert b"Se el primero" in res.data

    def test_route_signup(self):
        res = self.tester.get("/signup")
        assert res.status_code == 200
        assert b"Registro" in res.data


if __name__ == '__main__':
    unittest.main()
