from tests.base import BaseTestCase
from app.models import User, Destination, Country, Region, Continent
from app import db

class TestMain(BaseTestCase):
   def test_explored_and_favorites(self):
        cont = Continent(name='Asia', id=1)
        region = Region(name='Southeast Asia', id=1, cont_id=1)
        country = Country(name='Myanmar', id=1, region_id=1)
        dest = Destination(name='Bagan', id=1, country_id=1)
        u = User(email='jacob@example.com')

        db.session.add_all([cont, region, country, dest, u])
        db.session.commit()

        self.assertEqual(u.explored_dests.all(), [])
        self.assertEqual(u.favorited_dests.all(), [])

        u.alter_explored(dest)
        u.alter_favorite(dest)
        db.session.commit()
        self.assertTrue(u.has_explored(dest))
        self.assertTrue(u.has_favorited(dest))
        self.assertEqual(u.explored_dests.first().name, 'Bagan')
        self.assertEqual(u.favorited_dests.first().name, 'Bagan')
        self.assertEqual(dest.explored_users.first().email, 'jacob@example.com')
        self.assertEqual(dest.favorited_users.first().email, 'jacob@example.com')

        u.alter_explored(dest)
        u.alter_favorite(dest)
        self.assertFalse(u.has_explored(dest))
        self.assertFalse(u.has_favorited(dest))
        db.session.commit()