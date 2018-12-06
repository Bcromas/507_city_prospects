#507 final project
#Compare housing costs, startup environment, and cost of living between three U.S. cities.
import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

#caching functionality
CACHE_FNAME = 'final_proj_CACHE.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICT = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICT = {}
#end caching functionality

#start of class for capturing Zillow home details
class ZillowHome():
    def __init__(self, streetAddress, city=None, beds=None, baths=None, rooms=None, sqft=None, price=None, price_sqft=None, est_mortgage=None, url=None):
        self.streetAddress = streetAddress
        self.city = city
        self.beds = beds
        self.baths = baths
        self.rooms = rooms
        self.sqft = sqft
        self.price = price
        self.price_sqft = price_sqft
        # self.est_mortgage = est_mortgage
        self.url = url

    def __str__(self):
        return "{} - Price:{} - Price/SQFT:{}".format(self.streetAddress, self.price,self.price_sqft)
#end of class for capturing Zillow home details

#var for DB
DBNAME = 'city_prospects.db'

#start of funct to setup DB
def db_setup(DBNAME):
    #start of attempt to create DB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Exception as e:
        print("Error creating DB: ",e)
        conn.close()
    #end of attempt to create DB

    #start of attempt to drop Cities table
    try:
        statement = '''
        DROP TABLE IF EXISTS 'Cities';
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error dropping Cities table: ",e)
        conn.close()
    #end of attempt to drop Cities table

    #start of attempt to drop Houses table
    try:
        statement = '''
        DROP TABLE IF EXISTS 'Houses';
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error dropping Houses table: ",e)
        conn.close()
    #end of attempt to drop Houses table

    #start of attempt to create Cities table
    try:
        statement = '''
        CREATE TABLE 'Cities' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT,
        'State' TEXT
        );
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error creating Cities table: ",e)
        conn.close()
    #end of attempt to create Cities table

    #start of attempt to create Houses table
    try:
        statement = '''
        CREATE TABLE 'Houses' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Street Address' TEXT,
        'City' TEXT,
        'Price' REAL,
		CONSTRAINT fk_cities
		FOREIGN KEY ('City')
		REFERENCES Cities(Id)
        );
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error creating Houses table: ",e)
        conn.close()
    #end of attempt to create Houses table
#end of funct to setup DB

#start of funct to check DB for city, insert if needed, & return Cities record ID
def cities_id(city, state):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    city_id = ''

    try:
        statement = "SELECT Id from Cities WHERE Name='{}'".format(city.title())
        cur.execute(statement)
        x = cur.fetchall()
        if len(x) == 0:
            insertion = (None,city.title(),state.upper())
            statement = 'INSERT into Cities '
            statement += 'VALUES (?,?,?)'
            cur.execute(statement,insertion)
            conn.commit()

            city_id = cur.lastrowid

        else:
            city_id = x[0][0]

    except Exception as e:
        print("Error finding Cities record: ",e)

    return city_id
#end of funct to check DB for city, insert if needed, & return Cities record ID

#start of funct to insert House instances into DB
def houses_insert(house):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    try:
        insertion = (None, str(house.streetAddress), house.city, house.price)
        statement = 'INSERT into Houses '
        statement += 'VALUES (?,?,?,?)'
        cur.execute(statement,insertion)
        conn.commit()
    except Exception as e:
        print("Error inserting Houses record: ",e)
#end of funct to insert House instances into DB

#start of simple check of cache
def check_cache(url):

    if url in CACHE_DICT:
        print("Retrieving from cache...")
        return CACHE_DICT[url]
    else:
        print("Retrieving from site...")
        resp = requests.get(url, headers={'User-Agent': 'SI_CLASS'})
        CACHE_DICT[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICT)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICT[url]
#end of simple check of cache

#start of crawling Zillow for homes
def home_prices(city,city_id):
    city_id = city_id

    zil_base_url = 'https://www.zillow.com/homes/for_rent'
    zil_city_url = zil_base_url+"/"+city
    city_in_cache = check_cache(zil_city_url)
    city_soup = BeautifulSoup(city_in_cache,'html.parser')
    photo_cards = city_soup.find(class_="photo-cards")
    test_list = []
    url_list = []

    for i in photo_cards:
        try:
            home_url = i.a['href']
            if 'homedetails'in home_url:
                zil_home_url = zil_base_url+home_url
                url_list.append(zil_home_url)
            else:
                pass
        except Exception as e:
            # print('Error: ',e)
            pass
    for i in url_list:
        home_in_cache = check_cache(i)
        home_soup = BeautifulSoup(home_in_cache,'html.parser')

        zil_url = i #here's apt URL

        #FINDING STREET ADDRESS
        zil_streetAddressX = home_soup.find(class_ = "zsg-content-header addr")
        zil_streetAddressY = zil_streetAddressX.find('h1')
        zil_streetAddressZ = zil_streetAddressY.contents[0] #here's the actual street address
        zil_streetAddress_clean = zil_streetAddressZ.strip()
        print('original: ',zil_streetAddressZ)
        print('cleaned: ',zil_streetAddress_clean)
        print("*"*20)

        #FINDING PRICE
        zil_priceX = home_soup.find(class_ ="zsg-lg-1-3 zsg-md-1-1 hdp-summary")
        zil_priceY = zil_priceX.find(class_ ="main-row home-summary-row")
        zil_price = zil_priceY.find(class_ ="").contents[0] #here's the actual price

        #FINDING BEDS
        facts_expandable = home_soup.find(class_ ="hdp-facts-expandable-container clear") #one large section starting with 'Facts and Features'
        facts_columns = facts_expandable.find_all(class_ = "hdp-fact-container-columns") #multiple subsections containing grouped details on apt
        for i in facts_columns: #iterate through various subsections e.g. 'RENTAL FACTS' or 'INTERIOR FEATURES'
            fact_category = i.find(class_ = "hdp-fact-category") #grab all 'fact categories' a.k.a. apt details
            try:
                if fact_category.text == 'Bedrooms': #find apt detail with given title
                    zil_beds = fact_category.parent.find(class_="hdp-fact-value").text #go back up one level to grab actual value for apt detail with given title above
            except:
                pass

        #FINDING BATHS
        zil_bathsX = home_soup.find(class_ = "zsg-content-header addr")
        zil_bathsY = zil_bathsX.find_all(class_="addr_bbs")
        for i in zil_bathsY:
            if 'bath' in i.text:
                zil_bathsZ = i.text.split(' ')[0]
            else:
                pass

        #FINDING SQFT
        zil_sqftX = home_soup.find(class_ = "zsg-content-header addr")
        zil_sqftY = zil_sqftX.find_all(class_="addr_bbs")
        for i in zil_sqftY:
            if 'sqft' in i.text:
                zil_sqftZ = i.text.split(' ')[0]
            else:
                pass

        x = ZillowHome(streetAddress = zil_streetAddressZ, city = city_id, price = zil_price, beds = zil_beds, baths = zil_bathsZ, sqft = zil_sqftZ, url = zil_url)
        test_list.append(x)
    # for i in test_list:
        # print('street address: ',i.streetAddress)
        # print('city id: ',i.city)
        # print('price: ',i.price)
        # print('beds: ',i.beds)
        # print('baths: ',i.baths)
        # print('sqft: ',i.sqft)
        # print('URL: ',i.url)
        # print("*"*20)

        # houses_insert(i)


#end of crawling Zillow for homes

def graph_1(city_id): #pass in a list containing prices & a list containing sq ft

    # print('here is yo city',city_id)
    price_list = []
    sqft_list = []

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Price "
    statement += "FROM Houses "
    statement += "WHERE City = '{}'".format(city_id)
    cur.execute(statement)
    for i in cur:
        price_list.append(i[0])
        # some other variable(s)
    conn.close()

    # Create a trace
    trace = go.Scatter(
        # x = [450000,235000,171800],
        x = price_list,
        y = [2700,1308,860,743,2600,108,960,850],
        mode = 'markers'
    )

    data = [trace]

    #plot
    plot_url = py.plot(data, filename='basic-line')

if __name__ == "__main__":
    while True:
        # user_input = input('Please enter a U.S. city and state abbreviation\ne.g. "philadelphia-pa" ')
        user_input = input('Please enter a command\ne.g. "city_insert" ')

        if user_input.lower() == 'exit':
            break

        #to be consolidated later as 'start up' funct
        elif user_input.lower() == 'db_setup':
            db_setup()

        elif user_input.lower() == 'city_insert':
            while True:
                city_input = input('Enter your first city in format {City Name}-{State Abbrev}: ')
                if '-' in city_input:
                    city = city_input.split('-')[0]
                    state = city_input.split('-')[1]
                    find = cities_id(city,state) #holds the id of the relevant Cities record in DB
                    # print(find)
                    home_prices(city_input,find)
                if city_input.lower() == 'exit':
                    break

        elif user_input.lower() == 'graph_1':
            while True:
                graph1_input = input('Which city would you like to plot?\nPlease enter in format {City Name}-{State Abbrev}: ')
                if '-' in graph1_input:
                    city = graph1_input.split('-')[0]
                    state = graph1_input.split('-')[1]
                    try:
                        conn = sqlite3.connect(DBNAME)
                        cur = conn.cursor()
                        statement = "SELECT Id from Cities WHERE Name='{}' and State = '{}'".format(city.title(),state.upper())
                        cur.execute(statement)
                        x = cur.fetchall()
                        city_id = x[0][0]
                        graph_1(city_id)
                    except Exception as e:
                        print("Error querying DB: ",e)
                        conn.close()

                        # graph_1()
                if graph1_input.lower() == 'exit':
                    break
