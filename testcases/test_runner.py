import unittest
from django.conf import settings
from django.db.models import get_app, get_apps
from django.test import _doctest as doctest
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.testcases import OutputChecker, DocTestRunner

from django.test.simple import build_suite

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    Run the unit tests for all the test labels in the provided list.
    
    !!!
    This test runner work with REAL database, not with test!!!
    !!!

    When looking for tests, the test runner will look in the models and
    tests modules for the application.
    
    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.
    
    Returns the number of tests that failed.
    """
    setup_test_environment()
    
    settings.DEBUG = False    
    suite = unittest.TestSuite()
    
    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    else:
        for app in get_apps():
            suite.addTest(build_suite(app))
    
    for test in extra_tests:
        suite.addTest(test)

    old_name = settings.DATABASE_NAME    
    #connection.creation.create_test_db(verbosity, autoclobber=not interactive)
    result = unittest.TextTestRunner(verbosity=old_name).run(suite)
    #connection.creation.destroy_test_db(old_name, verbosity)
    
    teardown_test_environment()
    
    return len(result.failures) + len(result.errors)