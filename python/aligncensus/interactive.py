import requests

class QueryBuilder():
    """
    It's not a builder per se, but a helper class to get to the query parts
    Help data scientists browse the Census API available tables by
    theme or available variables
    Intended to be used in an interactive terminal or in a notebook, for example
    Do the job of parsing the metadata to answer likely questions.
    *  What tables are available with information on X?
    *  What columns are in those tables?
    *  What tables have columns like Y?
    *  What tables include a given year?
    *  What tables include a given location?
    """
    def __init__(self):
        self.base_url = "http://api.census.gov/data"

    def get_all_table_metadata(self):
        print("Querying Census for Table Data")
        response = requests.get(self.base_url)
        if response.status_code == 200:
            metadata = response.json()
        else:
            print(f"Can't query the census, most basic query {self.base_url} returned status code {response.status_code}")
        
        print("Assembling response into useful formats")
        num_entries = len(metadata['dataset'])
        self.table_titles = [metadata['dataset'][j]['title'] for j in range(num_entries)]
        self.table_descriptions = [metadata['dataset'][j]['description'] for j in range(num_entries)]
        print(f"Ready to search through {len(self.table_titles)} tables")
        
if __name__ == '__main__':
    qb = QueryBuilder()
    qb.get_all_table_metadata()
    