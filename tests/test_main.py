from tests.base import BaseTestCase
from app.models import User, Destination, Country, Region, Continent
from app import db

class TestMain(BaseTestCase):

  #This is more of an integration test. Probably better to break it out.
   def test_explored_and_favorites(self):
        dest = self.create_dest()
        u = self.register_user()

        db.session.add_all([dest, u])
        db.session.commit()

        self.assertEqual(u.explored_dests.all(), [])
        self.assertEqual(u.favorited_dests.all(), [])

        u.alter_explored(dest)
        u.alter_favorite(dest)
        db.session.commit()
        self.assertTrue(u.has_explored(dest))
        self.assertTrue(u.has_favorited(dest))
        self.assertEqual(u.explored_dests.first().name, dest.name)
        self.assertEqual(u.favorited_dests.first().name, dest.name)
        self.assertEqual(dest.explored_users.first().email, u.email)
        self.assertEqual(dest.favorited_users.first().email, u.email)

        u.alter_explored(dest)
        u.alter_favorite(dest)
        self.assertFalse(u.has_explored(dest))
        self.assertFalse(u.has_favorited(dest))
        db.session.commit()