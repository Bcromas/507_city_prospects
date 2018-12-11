# City Prospects
City Prospects is a program to help individuals compare rental markets between two U.S. cities based on data scraped from Zillow.com.

<!-- ![Rent & Square Footage in San Diego](https://github.com/Bcromas/507_city_prospects/blob/master/README_images/Rent%20SQFT%20Apts%20San%20Diego.png) -->

<img src="https://github.com/Bcromas/507_city_prospects/blob/master/README_images/Rent%20SQFT%20Apts%20San%20Diego.png" width="100" height="100">

## Usage & User Guide
Clone or download this repository, install any missing libraries (see [requirements.txt](https://github.com/Bcromas/507_city_prospects/blob/master/requirements.txt)), and run the city_prospects.py file.

You will need a Plot.ly account to view the visualizations and can follow the installation and setup instructions here: https://plot.ly/python/getting-started/

## Data Source & By-Products
The data is sourced by crawling and scraping up to 20 pages of search results for apartments for rent in a given city at Zillow.com. In terms of data by-products, a local cache is maintained in a JSON file for each Zillow.com page visited, and details captured on cities and apartments are stored in a SQLite database.

## Code

#### High-Level
In general the program operates in the following way: accept a U.S. city in the format {city name}-{state abbrev}, crawl up to 20 Zillow.com pages, process the data and create instances of apartments using ZillowHome(), insert details from ZillowHome() instances into a local SQLite database, and ultimately facilitate the generation of two classes of visualizations: details on one U.S. city and details comparing two U.S. cities.

#### Commands
**'Add city'** Crawl and scrape Zillow.com for apartments in a given city. *NOTE: can take several minutes.*

**'Visuals'** View data on a single city or compare two cities. Visualizations include:
1. Scatter plot of rent and square feet for a city.
2. Box plots of rent and square feet for a city.
3. Stacked bars comparing rent in 2 cities.
4. Table of averages comparing 2 cities.

**'Delete_db'** Delete and rebuild the SQLite database.

**'Exit'** Return to the previous screen or exit program if at the main menu.

#### Key Functions
**cities_id(city, state)** Expects two strings describing a city (city name and state abbreviation), checks the SQLite database for a match, inserts a new record if no match is found, and returns the id of the city.

**apartment_prices(city, city_id)** Expects a city name and the id of the related City record in the SQLite database, starts crawling at the first page of search results for the given city at https://www.zillow.com/homes/for_rent +city_name-state_abbrev, scrapes details for apartments from their individual pages, calls ZillowHome() to create instances of each apartment, inserts details from ZillowHome() instances into the SQLite database, and iterates through a maximum of 20 pages of search results.

**apartments_insert(house)** Expects a ZillowHome() instance, connects to the SQLite database, and attempts to insert apartment details into the database. All ZillowHome() instances/apartments inserted are related to a record in the City table.

**graph_1(city_id)** Expects the id of a City record in the SQLite database, connects to the SQLite database, queries details on related Apartment records, and calls Plot.ly to generate a scatter plot of rent and square feet in the given city.

**graph_2(city_id)** Expects the id of a City record in the SQLite database, connects to the SQLite database, queries details on related Apartment records, and calls Plot.ly to generate a box plot of rent and square feet in the given city.

**graph_3(city_idA, city_idB)** Expects the ids of two City records in the SQLite database, connects to the SQLite database, queries details on related Apartment records, and calls Plot.ly to generate a stacked bar chart comparing rent in the two given cities.

**graph_4(city_idA, city_idB)** Expects the ids of two City records in the SQLite database, connects to the SQLite database, queries details on related Apartment records, and calls Plot.ly to generate a table of averages comparing the two given cities.

**db_setup()** Expects no inputs. Will drop any existing City and Apartment tables in the SQLite database and then rebuild the database.

*Helper functions:* Several additional functions support the above including the selection of a random city from the database, caching pages crawled and scraped, and loading help text from a related .txt file among others.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
