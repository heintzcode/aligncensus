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
        check = cq.check_url()
        self.assertTrue(check[0])
        self.assertIsNone(check[1])

        request_url = "http://api.census.gov/not/a/valid/url"
        cq.set_census_database_url(request_url)
        check = cq.check_url()
        self.assertFalse(check[0])
        self.assertEqual(404, check[1])

        request_url = "http://api.census"
        cq.set_census_database_url(request_url)
        check = cq.check_url()
        self.assertFalse(check[0])
        self.assertEqual("ConnectionError", check[1])

    def testCensusVariableTest(self):
        cq = queries.CensusQuery()
        cq.set_census_database_url("http://api.census.gov/data/1994/zbp")
        cq.check_url()

        cvariable = "PAYQTR1"
        cq.set_census_variable(cvariable)
        cq.check_variable()
        
        cvariable = "PAYQTR2"
        cq.set_census_variable(cvariable)
        with self.assertRaises(AssertionError):
            cq.check_variable()

if __name__ == '__main__':
    unittest.main()

