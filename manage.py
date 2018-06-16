from flask_script import Manager
from app import create_app
import os

app = create_app()
manager = Manager(app)

@manager.command
def test():
    """Run all unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()