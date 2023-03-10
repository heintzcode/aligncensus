import os
import pandas as pd
import requests
from time import time

class CensusQuery():
    """
    Methods to help in querying the U.S. Census Data API, then align with another dataset
    Provides useful feedback if the query or alignment fails
    """
    def __init__(self):
        self.census_database_url = None
        self.census_variable = None
        self.censes_predicate = None
        self.census_api_key = None
        self.querychecker = QueryChecker()

    def set_census_database_url(self, url):
        """
        Sets the `census_database_url` field, which can be found here: https://api.census.gov/data.html
        A request can access only one database at a time.
        """
        self.census_database_url = url
        self.querychecker.url = url

    def set_census_variable(self, variable):
        """
        Sets the `census_variable` field, which is the column of data in the census database that is of interest
        Examples include age, ethnicity, income, etc. 
        """
        self.census_variable = variable
        self.querychecker.variable = variable

    def set_census_predicate(self, predicate):
        """
        Sets the `census_predicate` field, which specifies the subset of the database of interest
        This will typically be of the form "column_name:value,value,value...", where
        * column_name is a column in the census database, usually holding geographic information
        * values are a set derived from the user's dataframe that describe the same kind of geographic information
        It may also hold calendar information, to subset the census data to a certain timeframe.
        Instructions on predicate syntax are given in https://www.census.gov/content/dam/Census/data/developers/api-user-guide/api-guide.pdf
        Helper methods for creating the predicate are an aspiration for the AlignCensus library...
        """
        self.census_predicate = predicate
        self.querychecker.predicate = predicate

    def set_census_api_key(self, api_key_path=None):
        """
        Read the user's api key that can be obtained from: https://api.census.gov/data/key_signup.html
        Default path is a file called "census_api_key.txt" in the working directory
        """
        if api_key_path is None:
            api_key_path = os.path.join(os.path.dirname(__file__), "census_api_key.txt")
        with open(api_key_path, 'r') as keyfile:
            self.census_api_key = keyfile.readline().rstrip()
            self.querychecker.api_key = self.census_api_key

    def create_request(self, check_request):
        """
        First checks that all parts of the request are valid
        Slots the provided query parts into the correct syntax of a US Census API request
        """
        if check_request:
            self.querychecker.check_request()
        self.request = f"{self.census_database_url}?get={self.census_variable}&for={self.census_predicate}&key={self.census_api_key}"
    
    def response_code_is_good(self):
        """
        Parses the response to an API request for the status code only
        """
        if self.response.status_code == 200:
            return True, None
        else:
            return False, f"Request returned an error response, status code: {self.response.status_code}"
            
    def get_census_dataframe(self, check_request=True):
        """
        Make the request to the Census API for the data.
        Recommended to leave check_request as True, it's kind of the point of this class
        """
        self.create_request(check_request)
        print(f"Sending request (abbreviated): {self.request[:150]}")
        self.response = requests.get(self.request)
        if self.response_code_is_good():
            census_df = pd.DataFrame(self.response.json()[1:], columns=self.response.json()[0])
            print(f"Retrieved {census_df.shape[0]} rows with columns {census_df.columns}")
            return census_df
        
    def align_datasets(self, user_dataset: pd.DataFrame, user_dataset_geo_column: str, census_dataset: pd.DataFrame, census_dataset_geo_column: str):
        """
        Adds a column to the user_dataset with the requested information from the census_dataset, aligned by matching values in the two geo_columns.
        Uses `pd.DataFrame.join` to achieve this in a single call, no looping
        """
        return user_dataset.join(census_dataset.set_index(census_dataset_geo_column), on=user_dataset_geo_column)
    
class QueryChecker():
    def __init__(self):
        self.api_key = None
        self.url = None
        self.variable = None
        self.predicate = None 
        self.valid_variables = []
        self.valid_predicates = []

    def check_request(self):
        """
        Check each segment of the request in turn and provide helpful output if something fails
        """
        print("Checking validity of the Census API request (may take a moment if API is slow)")
        assert(self.api_key is not None), f"Set the census api key with `CensusQuery.set_census_api_key` before checking or making request"
        assert(self.url is not None), f"Set the database url with `CensusQuery.set_census_database_url` before checking or making request"
        self.check_url()
        assert(self.variable is not None), f"Set the requested variable with `CensusQuery.set_census_variable` before checking or making request"
        self.check_variable()
        assert(self.predicate is not None), f"Set the requested predicate with `CensusQuery.set_census_predicate` before checking or making request"
        self.check_predicate()

    def check_url(self):
        """
        Make a request to the US Census that returns a status 200 if the database URL is correct
        Collect some data from the metadata that is returned from the successful call to exploit later
        """
        request = f"{self.url}"
        try:
            response = requests.get(request)
        except requests.exceptions.ConnectionError as ce:
            raise(ce)
        
        if response.status_code == 200:
            cvars_link = response.json().get("dataset")[0].get("c_variablesLink")
            cvars_response = requests.get(cvars_link).json()
            for variable, terms in cvars_response['variables'].items():
                self.valid_predicates.append(variable)
                if "predicateOnly" in terms.keys() and terms["predicateOnly"] is True:
                    pass
                else:
                    self.valid_variables.append(variable)
        else:
            raise RuntimeError(f"Database URL is not valid, got response code {response.status_code}")

    def check_variable(self):
        """
        Ensure that the variable requested is one that is available in the requested database
        """
        assert(self.variable in self.valid_variables), f"Census variable not valid; for database {self.url} the variable must be one of {self.valid_variables}"

    def check_predicate(self):
        """
        Ensure that the name of the predicate is available in the requested database
        """
        colon_index = self.predicate.find(":")
        assert(colon_index > 0), f"Census predicate must begin with one of {self.valid_predicates} and end with ':'"
        assert(colon_index < len(self.predicate)-1), f"Census predicate must have values listed after ':'"
        assert(self.predicate[:colon_index] in self.valid_predicates), f"Census predicate '{self.predicate[:150]}...' not valid; for database {self.url} the predicate name must be one of {self.valid_predicates}"


if __name__ == '__main__':
    cq = CensusQuery()

    cq.set_census_api_key()

    # Get our data and verify the geo_column
    mydata_url = "https://data.cityofnewyork.us/resource/usc3-8zwd.csv"
    mydata_geo_column = "postcode"
    mydata_geo_column_str = f"{mydata_geo_column}_str"

    print("Reading user-defined dataset")
    my_df = pd.read_csv(mydata_url)
    my_df[mydata_geo_column_str] = my_df[mydata_geo_column].apply(lambda x: str(x))
    print(f"Read {my_df.shape[0]} rows, geo_column looks like: \n{my_df[mydata_geo_column_str][:10]}")
    
    census_database_url = "http://api.census.gov/data/1994/zbp"
    census_variable = "PAYQTR1"
    census_predicate = f"ZIPCODE:{','.join([i for i in set(my_df['postcode_str'])])}"

    cq.set_census_database_url(census_database_url)
    cq.set_census_variable(census_variable)
    cq.set_census_predicate(census_predicate)

    census_df = cq.get_census_dataframe()

    census_geo_column = "zipcode"
    my_df_enhanced = cq.align_datasets(my_df, mydata_geo_column_str, census_df, census_geo_column)
    print("Databases joined, items of interest:")    
    print(my_df_enhanced[[mydata_geo_column, census_variable]])

