# City Prospects
City Prospects is a program to help individuals compare rental markets between two U.S. cities based on data scraped from Zillow.com.

## Usage & User Guide
Clone or download this repository, install any missing libraries (see [requirements.txt](https://github.com/Bcromas/507_city_prospects/blob/master/requirements.txt)), and run the city_prospects.py file.

You will need a Plot.ly account to view the visualizations and can follow the installation and setup instructions here: https://plot.ly/python/getting-started/

## Data Source & By-Products
The data is sourced by crawling and scraping up to 20 pages of search results for apartments for rent in a given city at Zillow.com (https://www.zillow.com/homes/for_rent). In terms of data by-products, a local cache is created in a JSON file and details captured on cities and apartments are stored in a SQLite database.

## Code

#### High-Level
In general the program operates in the following high-level way: accept a U.S. city in the format {city name}-{state abbrev}, crawl up to 20 Zillow.com pages, process the data and create instances of apartments using ZillowHome(), insert details from ZillowHome() instances into a local SQLite database, and generate two classes of visualizations: details on one U.S. city or details comparing two U.S. cities.

#### Commands
**'Add city'** Crawl and scrape Zillow.com for apartments in a given city. *NOTE: can take several minutes.*

**'Visuals'** View data on a single city or compare two cities. Visualizations include:
1. Scatter plot of rent and square feet for a city.
2. Box plots of rent and square feet for a city.
3. Stacked bars comparing rent in 2 cities.
4. Table of averages comparing 2 cities.

**'Delete_db'** Delete and rebuild the DB.

**'Exit'** Return to previous screen or exit program if at main menu.

#### Key Functions
**cities_id(city, state)** Expects two strings describing a city (city name and state abbreviation), checks the SQLite database for a match or inserts a new record if no match is found, and returns the id of the city.

**apartment_prices(city, city_id)** Expects a city name and the id of the related City record in the SQLite database, starts crawling at the first page of search results for the given city starting at https://www.zillow.com/homes/for_rent +city_name-state_abbrev, scrapes details for apartments from their individual pages, calls ZillowHome() to create instances of each apartment, inserts details from ZillowHome() instances into the SQLite databse, and iterates through a maximum of 20 pages of search results.

**apartments_insert(house)** Expects a ZillowHome() instance, connects to SQLite database, and attempts to insert apartment details into the database. 

**graph_1(city_id)**

**graph_2(city_id)**

**graph_3(city_idA, city_idB)**

**graph_4(city_idA, city_idB)**

**db_setup()**

*Helper functions:* Several additional functions support the above including the selection of a random city from the database, caching pages crawled and scraped, and loading help text from a related .txt file among others.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
