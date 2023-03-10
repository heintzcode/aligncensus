# aligncensus
Align data from the US Census databases with your own data, using geographic information available in both.

`python/aligncensus/interactive.ipynb` will allow you to browse the census tables for the one that has the right type of information for you, and will start to help you build a query for that.

`python/aligncensus/manual_example.ipynb` will show you how to build up a request to the US Census API, create a dataframe from the result, and then align that result with your own data in a new column.

`python/aligncensus/queries.py` contains two classes for building and checking a query to the Census API. Following the example may save you some time in query building because you will get slightly more informative feedback than if you use trial and error on your requests without these helper classes.
