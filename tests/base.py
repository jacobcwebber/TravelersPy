from app import create_app, db
from flask_testing import TestCase
from config import TestConfig
from faker import Faker
from app.models import User, Destination, Country

class BaseTestCase(TestCase):
    def create_app(self):
        """Create an instance of the app with the testing configuration."""
        return create_app(TestConfig)

    def setUp(self):
        """Create the database and initialize faker."""
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.commit()
        self.faker = Faker()

    def tearDown(self):
        """Remove ression and drop the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()   

    def register_user(self):
        return User(
            first_name = self.faker.first_name(),
            last_name = self.faker.last_name(),
            email = self.faker.email(),
            password = self.faker.password()
        )
    
    def create_destination(self, name):
        return Destination(
            name = name,
            description = self.faker.text(),
            update_date = self.faker.past_datetime()
        )
    
    def create_country(self):
        return Country(
            name = self.faker.country()
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)