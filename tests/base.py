from app import create_app, db
from flask_testing import TestCase
from config import TestConfig

class BaseTestCase(TestCase):
    def create_app(self):
        """Create an instance of the app with the testing configuration."""

        return create_app(TestConfig)

    def setUp(self):
        """Create the database."""
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """Remove ression and drop the database."""

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

if __name__ == '__main__':
    unittest.main(verbosity=2)