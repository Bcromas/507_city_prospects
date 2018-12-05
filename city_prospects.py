#507 final project
#Compare housing costs, startup environment, and cost of living between three U.S. cities.
import requests
import json
from bs4 import BeautifulSoup
import sqlite3

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
        self.est_mortgage = est_mortgage
        self.url = url

    def __str__(self):
        return "{} - Price:{} - Price/SQFT:{}".format(self.streetAddress, self.price,self.price_sqft)
#end of class for capturing Zillow home details

#var for DB
DBNAME = 'city_prospects.db'

#start of funct to setup DB
def db_setup():
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

    state_id = ''

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

            state_id = cur.lastrowid

        else:
            state_id = x[0][0]

    except Exception as e:
        print("Error finding Cities record: ",e)

    return state_id
#end of funct to check DB for city, insert if needed, & return Cities record ID

#start of funct to insert House instances into DB
def houses_insert(house):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    try:
        insertion = (None, house.streetAddress, house.city, house.price)
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
def home_prices(city,state_id):
    state_id = state_id

    zil_base_url = 'https://www.zillow.com/homes/for_sale'
    zil_city_url = zil_base_url+"/"+city
    city_in_cache = check_cache(zil_city_url)
    city_soup = BeautifulSoup(city_in_cache,'html.parser')
    photo_cards = city_soup.find(class_="photo-cards")
    test_list = []
    for i in photo_cards:
        # home_url = i.a['href']
        # zil_home_url = zil_base_url+home_url
        # home_in_cache = check_cache(zil_home_url)
        # home_soup = BeautifulSoup(home_in_cache,'html.parser')
        # zil_streetAddress = home_soup.find(class_ = "zsg-h1 hdp-home-header-st-addr").text
        # zil_price = home_soup.find(class_ = "price").text
        # zil_price_sqft = home_soup.find(id="yui_3_18_1_1_1543870631025_6979")
        # print(zil_price_sqft)

        try:
            home_url = i.a['href']
            zil_home_url = zil_base_url+home_url
            home_in_cache = check_cache(zil_home_url)
            home_soup = BeautifulSoup(home_in_cache,'html.parser')
            zil_streetAddress = home_soup.find(class_ = "zsg-h1 hdp-home-header-st-addr").text
            zil_price = home_soup.find(class_ = "price").text
            # zil_price_sqft = home_soup.find(class_ = "zsg-media-bd").text
            # zil_price_sqft = home_soup.find(class_ = "'category-group-name' id='yui_3_18_1_1_1543870631025_6979'").text
            # x = ZillowHome(streetAddress = zil_streetAddress, price = zil_price, price_sqft = zil_price_sqft)
            x = ZillowHome(streetAddress = zil_streetAddress, city = state_id, price = zil_price)
            test_list.append(x)
            #call ZillowHome with streetAddress, beds, baths, rooms, sqft, price, price_sqft, est_mortgage, url=None)

        except:
            pass

    for i in test_list: #continue adding attributes from home page to call to ZillowHome(), uncomment line 59,
        # print(i)
        houses_insert(i)
#end of crawling Zillow for homes

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
                city_input = input('Enter your first city in format {City Name}-{State Abbrev} ')
                if '-' in city_input:
                    city = city_input.split('-')[0]
                    state = city_input.split('-')[1]
                    find = cities_id(city,state) #holds the id of the relevant Cities record in DB
                    # print(find)
                    home_prices(city_input,find)
                if city_input.lower() == 'exit':
                    break
                # else:
                #     home_prices(city_input)
        # elif user_input.lower() == 'house_insert':
        #     test = ZillowHome(streetAddress = '216 Winthrop Rd', city = '8', price = 95800)
        #     houses_insert(test)


        # else:
        #     home_prices(user_input)
