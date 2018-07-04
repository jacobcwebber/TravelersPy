from app import create_app, db
from flask_testing import TestCase
from config import TestConfig
from faker import Faker
from random import randint
from app.models import User, Destination, Country, Region, Continent

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
    
    def create_dest(self):
        country_id = self.create_country().id
        dest =  Destination(
            id = randint(0,100),
            name = self.faker.state(),
            description = self.faker.text(),
            update_date = self.faker.past_datetime(),
            country_id = country_id
        )
        return dest
    
    def create_country(self):
        region_id = self.create_region().id
        country =  Country(
            id = randint(0,100),
            name = self.faker.country(),
            region_id = region_id
        )
        db.session.add(country)
        db.session.commit()
        return country

    def create_region(self):
        cont_id = self.create_cont().id
        region = Region(
            id = randint(0,100),
            name = self.faker.state(),
            cont_id = cont_id
        )
        db.session.add(region)
        db.session.commit()
        return region
    
    def create_cont(self):
        cont = Continent(
            id = randint(0,100),
            name = self.faker.state()
        )
        db.session.add(cont)
        db.session.commit()
        return cont

if __name__ == '__main__':
    unittest.main(verbosity=2)