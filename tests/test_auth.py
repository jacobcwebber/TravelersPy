from tests.base import BaseTestCase
from app.models import User, Destination, Country, Region, Continent
from app import db
import unittest
import time

class TestAuthBlueprint(BaseTestCase):
    def test_user_registration(self):
        """Test that a user is successfully created through the site."""
        
        u = User(email='test@example.com', password='password')
        

    def test_password_hashing(self):
        u = User(email='test@example.com')
        u.set_password('password')
        self.assertFalse(u.check_password('passw0rd'))
        self.assertTrue(u.check_password('password'))

    def test_password_salts_are_random(self):
        u = self.register_user('test@example.com', )


    def test_avatar(self):
        u = User(email='jacob@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '7a140783d558a1814a38a3bf7ed5f204'
                                         '?d=identicon&s=128'))
    
    def test_explored_and_favorites(self):
        cont = Continent(name='Asia', id=1)
        region = Region(name='Southeast Asia', id=1, cont_id=1)
        country = Country(name='Myanmar', id=1, region_id=1)
        dest = Destination(name='Bagan', id=1, country_id=1)
        u = User(email='jacob@example.com')

        db.session.add_all([cont, region, country, dest, user])
        db.session.commit()

        self.assertEqual(u.explored_dests.all(), [])
        self.assertEqual(u.favorited_dests.all(), [])

        u.add_explored(dest)
        u.add_favorite(dest)
        db.session.commit()
        self.assertTrue(u.has_explored(dest))
        self.assertTrue(u.has_favorited(dest))
        self.assertEqual(u.explored_dests.first().name, 'Bagan')
        self.assertEqual(u.favorited_dests.first().name, 'Bagan')
        self.assertEqual(dest.explored_us.first().email, 'jacob@example.com')
        self.assertEqual(dest.favorited_us.first().email, 'jacob@example.com')

        u.remove_explored(dest)
        u.remove_favorite(dest)
        db.session.commit()