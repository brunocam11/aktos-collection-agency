"""
Test suite for the accounts application.

This package contains tests for models, API endpoints, and services.
To run all tests for this app: python manage.py test accounts
To run only model tests: python manage.py test accounts.tests.models
To run only API tests: python manage.py test accounts.tests.api
To run only service tests: python manage.py test accounts.tests.services
"""

# Import test modules
from accounts.tests.models import *
from accounts.tests.api import *
from accounts.tests.services import *
