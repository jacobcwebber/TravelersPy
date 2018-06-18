from tests.base import BaseTestCase
from app.models import User, Destination, Country, Region, Continent
from app import db

class TestAuth(BaseTestCase):
    def test_user_registration(self):  
        user = User(
            first_name = self.faker.first_name(),
            last_name = self.faker.last_name(),
            email = self.faker.email(),
            password = self.faker.password()
        )
        db.session.add(user)
        db.session.commit()
        registered_user = User.query.filter_by(email=user.email).first()
        self.assertIsNotNone(registered_user)

    def test_password_hashing(self):
        u = User(email='test@example.com', password='password')
        self.assertFalse(u.check_password('passw0rd'))
        self.assertTrue(u.check_password('password'))

    def test_password_salts_are_random(self):
        u1 = User(email='test@example.com', password='password')
        u2 = User(email='test2@example.com', password='password')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_avatar(self):
        u = User(email='jacob@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '7a140783d558a1814a38a3bf7ed5f204'
                                         '?d=identicon&s=128'))
    