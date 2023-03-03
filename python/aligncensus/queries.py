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

    def create_request(self):
        """
        Slots the provided query parts into the correct syntax of a US Census API request
        """
        assert(self.census_database_url is not None), "Use censusquery.add_census_database_url(url) before calling `create_request`"
        assert(self.census_variable is not None), "Use censusquery.add_census_variable(variable) before calling `create_request`"
        assert(self.census_predicate is not None), "Use censusquery.add_census_predicate(predicate) before calling `create_request`"
        assert(self.census_api_key is not None), "Use censusquery.add_census_api_key(key) before calling `create_request`"
        self.request = f"{self.census_database_url}?get={self.census_variable}&for={self.census_predicate}&key={self.census_api_key}"
    
    def set_census_database_url(self, url):
        """
        Sets the `census_database_url` field, which can be found here: https://api.census.gov/data.html
        A request can access only one database at a time.
        """
        self.census_database_url = url

    def check_url(self):
        """
        Make a request to the US Census that returns a status 200 if the database URL is correct
        """
        request = f"{self.census_database_url}"
        try:
            response = requests.get(request)
        except requests.exceptions.ConnectionError:
            return False, "ConnectionError"
        
        if response.status_code == 200:
            cvars_link = response.json().get("dataset")[0].get("c_variablesLink")
            cvars_response = requests.get(cvars_link).json()
            self.valid_census_variables = []
            for variable, terms in cvars_response['variables'].items():
                if "predicateOnly" in terms.keys() and terms["predicateOnly"] is True:
                    pass
                else:
                    self.valid_census_variables.append(variable)
            return True, None
        else:
            return False, response.status_code

    def set_census_variable(self, variable):
        """
        Sets the `census_variable` field, which is the column of data in the census database that is of interest
        Examples include age, ethnicity, income, etc. 
        Set `check_variable` to True to test that the variable is valid in the assigned dataset
        """
        self.census_variable = variable

    def check_variable(self):
        """
        Make a request to the US Census that returns a status of 200 if the requested variable is valid 
        Requires that the `census_database` field has been set
        """
        assert(self.census_database_url is not None), "Set the census database url field first"
        assert(self.valid_census_variables is not None), "Get the valid census variables for this db using check_url()"
        assert(self.census_variable in self.valid_census_variables), f"Census variable not valid; for database {self.census_database_url} the variable must be one of {self.valid_census_variables}"

    def set_census_predicate(self, predicate, check_predicate=False):
        """
        Sets the `census_predicate` field, which specifies the subset of the database of interest
        This will typically be of the form "column_name:value,value,value...", where
        * column_name is a column in the census database, usually holding geographic information
        * values are a set derived from the user's dataframe that describe the same kind of geographic information
        It may also hold calendar information, to subset the census data to a certain timeframe.
        Instructions on predicate syntax are given in https://www.census.gov/content/dam/Census/data/developers/api-user-guide/api-guide.pdf
        Helper methods for creating the predicate are an aspiration for the AlignCensus library...
        Set `check_predicate` to True to test that the predicate is valid in the assigned dataset
        """
        self.census_predicate = predicate
        if check_predicate:
            self.check_predicate()

    def check_predicate(self):
        """
        Makes a request to the US Census that returns a status of 200 if the requested predicate is valid
        Requires that the `census_database` and `census_variable` fields have been set
        """
        pass

    def set_census_api_key(self, api_key_path=None):
        """
        Read the user's api key that can be obtained from: https://api.census.gov/data/key_signup.html
        Default path is a file called "census_api_key.txt" in the working directory
        """
        if api_key_path is None:
            api_key_path = os.path.join(os.path.dirname(__file__), "census_api_key.txt")
        with open(api_key_path, 'r') as keyfile:
            self.census_api_key = keyfile.readline().rstrip()

    def response_code_is_good(self):
        """
        Parses the response to an API request for the status code only
        """
        if self.response.status_code == 200:
            return True, None
        else:
            return False, f"Request returned an error response, status code: {self.response.status_code}"
            
    def get_census_dataframe(self):
        self.create_request()
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
    census_predicate = f"zipcode:{','.join([i for i in set(my_df['postcode_str'])])}"

    cq.set_census_database_url(census_database_url)
    cq.set_census_variable(census_variable)
    cq.set_census_predicate(census_predicate)

    census_df = cq.get_census_dataframe()

    census_geo_column = "zipcode"
    my_df_enhanced = cq.align_datasets(my_df, mydata_geo_column_str, census_df, census_geo_column)
    print("Databases joined, items of interest:")    
    print(my_df_enhanced[[mydata_geo_column, census_variable]])

