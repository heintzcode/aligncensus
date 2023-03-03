from aligncensus import queries
import pandas as pd
import unittest
import requests

class QueryTestTests(unittest.TestCase):
    """
    These are tests of the modules that run tests for the user
    """
    def testCensusURLtest(self):
        cq = queries.CensusQuery()

        request_url = "http://api.census.gov/data/1994/zbp"
        cq.set_census_database_url(request_url)
        cq.querychecker.check_url()

        request_url = "http://api.census.gov/not/a/valid/url"
        cq.set_census_database_url(request_url)
        with self.assertRaises(RuntimeError):
            cq.querychecker.check_url()

        request_url = "http://api.census"
        cq.set_census_database_url(request_url)
        with self.assertRaises(requests.exceptions.ConnectionError):
            cq.querychecker.check_url()
        
        request_url = ""
        cq.set_census_database_url(request_url)
        with self.assertRaises(requests.exceptions.MissingSchema):
            cq.querychecker.check_url()
        
    def testCensusVariableTest(self):
        cq = queries.CensusQuery()
        cq.set_census_database_url("http://api.census.gov/data/1994/zbp")
        cq.querychecker.check_url()

        cvariable = "PAYQTR1"
        cq.set_census_variable(cvariable)
        cq.querychecker.check_variable()
        
        cvariable = "PAYQTR2"
        cq.set_census_variable(cvariable)
        with self.assertRaises(AssertionError):
            cq.querychecker.check_variable()

    def testCensusPredicateTest(self):
        cq = queries.CensusQuery()
        cq.set_census_database_url("http://api.census.gov/data/1994/zbp")
        cq.querychecker.check_url()

        cpredicate = "ZIPCODE"
        cq.set_census_predicate(cpredicate)
        cq.querychecker.check_predicate()

        cpredicate = "GEO_ID"
        cq.set_census_predicate(cpredicate)
        cq.querychecker.check_predicate()

        cpredicate = "CO"
        cq.set_census_predicate(cpredicate)
        with self.assertRaises(AssertionError):
            cq.querychecker.check_predicate()

    def testQueryChecker(self):
        cq = queries.CensusQuery()
        cq.set_census_api_key()
        cq.set_census_database_url("http://api.census.gov/data/1994/zbp")
        cq.set_census_variable("PAYQTR1")
        cq.set_census_predicate("ZIPCODE")

        # Nothing happens if there's a good request
        cq.querychecker.check_request()
        cq.set_census_predicate("BAD_PRED")
        with self.assertRaises(AssertionError):
            cq.querychecker.check_request()

        cq.set_census_predicate("ZIPCODE")
        cq.set_census_variable("BAD_VAR")
        with self.assertRaises(AssertionError):
            cq.querychecker.check_request()
        
        cq.set_census_variable("PAYQTR1")
        cq.set_census_database_url("http://api.census.gov/bad/url")
        with self.assertRaises(RuntimeError) as re:
            cq.querychecker.check_request()
            self.assertEqual(re.msg, "Database URL is not valid, got response code 404")
            
if __name__ == '__main__':
    unittest.main()

