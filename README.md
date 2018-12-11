# City Prospects
City Prospects is a program to help individuals compare rental markets between two U.S. cities based on data scraped from Zillow.com.

## Usage & User Guide
Clone or download this repository, install any missing libraries (see [requirements.txt](https://github.com/Bcromas/507_city_prospects/blob/master/requirements.txt)), and run the city_prospects.py file.

You will need a Plot.ly account to view the visualizations and can follow the installation and setup instructions here: https://plot.ly/python/getting-started/

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Data Source & By-Products
The data is sourced by crawling and scraping up to 20 pages of search results for apartments for rent in a given city at Zillow.com (https://www.zillow.com/homes/for_rent). In terms of data by-products, a local cache is created in a JSON file and details captured on cities and apartments are stored in a SQLite database.

## Code
In general the program operates in the following high-level way: accept a U.S. city in the format {city name}-{state abbrev}, crawl up to 20 Zillow.com pages, process the data and create instances of ZillowHome(), insert details from ZillowHome() instances into a local SQLite database, and generate two classes of visualizations: details on one U.S. city or details comparing two U.S. cities.

**'Add city'** Crawl and scrape Zillow.com for apartments in a given city. *NOTE: can take several minutes.*

**'Visuals'** View data on a single city or compare two cities. Visualizations include:
1. Scatter plot of rent and square feet for a city.
2. Box plots of rent and square feet for a city.
3. Stacked bars comparing rent in 2 cities.
4. Table of averages comparing 2 cities.

**'Delete_db'** Delete and rebuild the DB.

**'Exit'** Return to previous screen or exit program if at main menu.

*Helper functions:* Several additional functions support the above including the selection of a random city from the database and caching pages crawled and scraped among others.
