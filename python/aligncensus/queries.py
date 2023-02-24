import os
import pandas as pd
import requests
from time import time

def get_census_api_key():
    with open(os.path.join(os.path.dirname(__file__), "census_api_key.txt"), "r") as keyfile:
        census_api_key = keyfile.readline().rstrip()
    return census_api_key

class CensusQuery():
    def __init__(self):
        self.census_database_url = None
        self.census_variable = None
        self.censes_predicate = None
        self.census_api_key = None

    def create_request(self):
        self.request = f"{self.census_database_url}?get={self.census_variable}&for={self.census_predicate}&key={self.census_api_key}"
    
    def add_census_database_url(self, url):
        self.census_database_url = url

    def add_census_variable(self, variable):
        self.census_variable = variable

    def add_census_predicate(self, predicate):
        self.census_predicate = predicate

    def add_census_api_key(self, key):
        self.census_api_key = key

    def response_code_is_good(self):
        if self.response.status_code == 200:
            return True
        else:
            print(f"Cannot create dataframe. Request returned an error response, status code: {self.response.status_code}")
            return False
            
    def get_census_dataframe(self):
        self.create_request()
        print(f"Sending request (abbreviated): {self.request[:150]}")
        self.response = requests.get(self.request)
        if self.response_code_is_good():
            census_df = pd.DataFrame(self.response.json()[1:], columns=self.response.json()[0])
            print(f"Retrieved {census_df.shape[0]} rows with columns {census_df.columns}")
            return census_df

census_api_key = get_census_api_key()
mydata_url = "https://data.cityofnewyork.us/resource/usc3-8zwd.csv"
mydata_geo_column = "postcode"
mydata_geo_column_str = f"{mydata_geo_column}_str"

# Get our data and verify the geo_column
print("Reading data of interest")
my_df = pd.read_csv(mydata_url)
my_df[mydata_geo_column_str] = my_df[mydata_geo_column].apply(lambda x: str(x))
print(f"Read {my_df.shape[0]} rows, geo_column looks like: \n{my_df[mydata_geo_column_str][:10]}")

cq = CensusQuery()

census_database_url = "http://api.census.gov/data/1994/zbp"
census_variable = "PAYQTR1"
census_predicate = f"zipcode:{','.join([i for i in set(my_df['postcode_str'])])}"

cq.add_census_api_key(census_api_key)
cq.add_census_database_url(census_database_url)
cq.add_census_variable(census_variable)
cq.add_census_predicate(census_predicate)

census_df = cq.get_census_dataframe()

census_geo_column = "zipcode"
my_df_enhanced = my_df.join(census_df.set_index(census_geo_column), on=mydata_geo_column_str)
print("Databases joined, items of interest:")    
print(my_df_enhanced[[mydata_geo_column, census_variable]])

