import unittest

from webapp import create_app
from webapp.models import db, User, Role
from webapp.extensions import admin, rest_api


class TestURLs(unittest.TestCase):
    def setUp(self):
        # Bug workarounds
        admin._views = []
        rest_api.resources = []

        app = create_app('webapp.config.TestConfig')
        self.client = app.test_client()

        # Bug workaround
        db.app = app

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_root_redirect(self):
        """ Tests if the root URL gives a 302 """

        result = self.client.get('/')
        self.assertEqual(result.status_code, 302)
        self.assertIn("/blog/", result.headers['Location'])

    def test_blog_home(self):
        """ Tests if the blog home page returns successfully """

        result = self.client.get('/blog/')
        self.assertEqual(result.status_code, 200)

    def test_login(self):
        """ Tests if the login form works correctly """

        test_role = Role("default")
        db.session.add(test_role)
        db.session.commit()

        test_user = User("test")
        test_user.set_password("test")
        db.session.add(test_user)
        db.session.commit()

        result = self.client.post('/login', data=dict(
            username='test',
            password="test"
        ), follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('You have been logged in', result.data)

    def test_logout(self):
        """ Tests if the login form works correctly """

        test_role = Role("default")
        db.session.add(test_role)
        db.session.commit()

        test_user = User("test")
        test_user.set_password("test")
        db.session.add(test_user)
        db.session.commit()

        result = self.client.post('/login', data=dict(
            username='test',
            password="test"
        ), follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('You have been logged in', str(result.data))

        result = self.client.get('/logout', follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('You have been logged out', str(result.data))

if __name__ == '__main__':
    unittest.main()
