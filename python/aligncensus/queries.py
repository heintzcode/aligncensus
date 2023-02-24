import os
import pandas as pd
import requests
from time import time

def get_census_api_key():
    with open(os.path.join(os.path.dirname(__file__), "census_api_key.txt"), "r") as keyfile:
        census_api_key = keyfile.readline().rstrip()
    return census_api_key

census_api_key = get_census_api_key()
mydata_url = "https://data.cityofnewyork.us/resource/usc3-8zwd.csv"
mydata_geo_column = "postcode"
mydata_geo_column_str = f"{mydata_geo_column}_str"

# Get our data and verify the geo_column
print("Reading data of interest")
my_df = pd.read_csv(mydata_url)
my_df[mydata_geo_column_str] = my_df[mydata_geo_column].apply(lambda x: str(x))
print(f"Read {my_df.shape[0]} rows, geo_column looks like: \n{my_df[mydata_geo_column_str][:10]}")


census_database_url = "http://api.census.gov/data/1994/zbp"
census_variable = "PAYQTR1"
census_predicate = "zipcode:{}".format(",".join([str(i) for i in range(10000,10999)]))
# The above range works, but is not complete in the mydata dataframe
# Create the predicate using exactly the postcodes in the data, of which there are less than 200 unique
census_predicate = f"zipcode:{','.join([i for i in set(my_df['postcode_str'])])}"
census_geo_column = "zipcode"

# Get the census data of interest and pull it into a dataframe
request = f"{census_database_url}?get={census_variable}&for={census_predicate}&key={census_api_key}"
print(f"Sending request (abbreviated): {request[:150]}")
t1 = time()
response = requests.get(request)
t2 = time()
print(f"Response received in {(t2-t1)} seconds")
if response.status_code != 200:
    print(f"Request returned an error response, status code: {response.status_code}")

else:
    census_df = pd.DataFrame(response.json()[1:], columns=response.json()[0])
    print(f"Retrieved {census_df.shape[0]} rows with columns {census_df.columns}")

# align the two datasets along the two geographic columns 
# make a new column that contains the correct value of interest for each value in
# my data's geographic column
my_df_enhanced = my_df.join(census_df.set_index(census_geo_column), on=mydata_geo_column_str)
print("Databases joined, items of interest:")    
print(my_df_enhanced[[mydata_geo_column, census_variable]])

