import os
import unittest
from app import create_app, db
from app.models import User, Destination, Country, Region, Continent
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URL')

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User(email='mackenzie@example.com')
        user.set_password('password')
        self.assertFalse(user.check_password('passw0rd'))
        self.assertTrue(user.check_password('password'))

    def test_avatar(self):
        user = User(email='jacob@example.com')
        self.assertEqual(user.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '7a140783d558a1814a38a3bf7ed5f204'
                                         '?d=identicon&s=128'))
    
    def test_explored_and_favorites(self):
        cont = Continent(name='Asia', id=1)
        region = Region(name='Southeast Asia', id=1, cont_id=1)
        country = Country(name='Myanmar', id=1, region_id=1)
        dest = Destination(name='Bagan', id=1, country_id=1)
        user = User(email='jacob@example.com')

        db.session.add_all([cont, region, country, dest, user])
        db.session.commit()

        self.assertEqual(user.explored_dests.all(), [])
        self.assertEqual(user.favorited_dests.all(), [])

        user.add_explored(dest)
        user.add_favorite(dest)
        db.session.commit()
        self.assertTrue(user.has_explored(dest))
        self.assertTrue(user.has_favorited(dest))
        self.assertEqual(user.explored_dests.first().name, 'Bagan')
        self.assertEqual(user.favorited_dests.first().name, 'Bagan')
        self.assertEqual(dest.explored_users.first().email, 'jacob@example.com')
        self.assertEqual(dest.favorited_users.first().email, 'jacob@example.com')

        user.remove_explored(dest)
        user.remove_favorite(dest)
        db.session.commit()

    def test

if __name__ == '__main__':
    unittest.main(verbosity=2)