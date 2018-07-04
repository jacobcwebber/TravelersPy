from tests.base import BaseTestCase
from app.models import User
from app import db
import time

class TestAuth(BaseTestCase):
    def test_create_user(self):  
        u = self.register_user()
        self.assertIsNotNone(u)

    def test_password_not_callable(self):
        u = self.register_user()
        self.assertRaises(AttributeError, lambda: u.password)

    def test_password_hashing(self):
        u = User(email='test@example.com', password='password')
        self.assertFalse(u.check_password('passw0rd'))
        self.assertTrue(u.check_password('password'))

    def test_password_salts_are_random(self):
        u1 = User(email='test@example.com', password='password')
        u2 = User(email='test2@example.com', password='password')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = self.register_user()
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm_account(token))

    def test_invalid_confirmation_token(self):
        u1 = self.register_user()
        u2 = self.register_user()
        db.session.add_all([u1, u2])
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm_account(token))

    def test_expired_confirmation_token(self):
        u = self.register_user()
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm_account(token))

    def test_avatar(self):
        u = User(email='jacob@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '7a140783d558a1814a38a3bf7ed5f204'
                                         '?d=identicon&s=128'))
    