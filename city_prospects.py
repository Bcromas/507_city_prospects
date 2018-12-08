#507 final project
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
    def __init__(self, streetAddress, city=None, beds=None, baths=None, sqft=None, price=None, url=None):
        self.streetAddress = streetAddress
        self.city = city
        self.beds = beds
        self.baths = baths
        if sqft == "":
            self.sqft = None
        else:
            self.sqft = sqft
        self.price = price
        if sqft == "":
            self.price_sqft = None
        elif (self.sqft.isdigit() and self.price.isdigit()):
            self.price_sqft = round(int(self.price)/int(self.sqft),3)
        else:
            self.price_sqft = None
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

    #start of attempt to drop Apartments table
    try:
        statement = '''
        DROP TABLE IF EXISTS 'Apartments';
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error dropping Apartments table: ",e)
        conn.close()
    #end of attempt to drop Apartments table

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

    #start of attempt to create Apartments table
    try:
        statement = '''
        CREATE TABLE 'Apartments' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Street Address' TEXT,
        'City' TEXT,
        'Price' REAL,
        'Beds' INTEGER,
        'Baths' INTEGER,
        'SQFT' INTEGER,
        'Price/SQFT' REAL,
        'URL' TEXT,
		CONSTRAINT fk_cities
		FOREIGN KEY ('City')
		REFERENCES Cities(Id)
        );
        '''
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Error creating Apartments table: ",e)
        conn.close()
    #end of attempt to create Apartments table
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
def apartments_insert(house):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    try:
        insertion = (None, house.streetAddress, house.city, house.price, house.beds, house.baths, house.sqft, house.price_sqft, house.url)
        statement = 'INSERT into Apartments '
        statement += 'VALUES (?,?,?,?,?,?,?,?,?)'
        cur.execute(statement,insertion)
        conn.commit()
    except Exception as e:
        print("Error inserting Apartments record: ",e)
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
def apartment_prices(city,city_id):
    city_id = city_id

    for i in range(0,9):
        try:
            page = i+1

            zil_base_url = 'https://www.zillow.com/homes/for_rent'
            zil_city_url = zil_base_url+"/"+city+"/"+str(page)+"_p"
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
                zil_streetAddressZ = str(zil_streetAddressY.contents[0]) #here's the actual street address
                zil_streetAddress_clean = zil_streetAddressZ.strip()
                if zil_streetAddress_clean[-1] == ',':
                    zil_streetAddress_cleaner = zil_streetAddress_clean[:-1]
                else:
                    zil_streetAddress_cleaner = zil_streetAddress_clean

                #FINDING PRICE
                zil_priceX = home_soup.find(class_ ="zsg-lg-1-3 zsg-md-1-1 hdp-summary")
                zil_priceY = zil_priceX.find(class_ ="main-row home-summary-row")
                zil_price = zil_priceY.find(class_ ="").contents[0] #here's the actual price
                zil_price_clean = zil_price.replace("+","").replace("$","").replace(" ","").replace(",", "")

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
                zil_sqftZ_clean = zil_sqftZ.replace(",","").replace("-","")

                x = ZillowHome(streetAddress = zil_streetAddress_cleaner, city = city_id, price = zil_price_clean, beds = zil_beds, baths = zil_bathsZ, sqft = zil_sqftZ_clean, url = zil_url)
                print(x)
                test_list.append(x)
            for i in test_list:
                apartments_insert(i)
        except Exception as e:
            print('Error crawling pages',e)
#end of crawling Zillow for homes

#start of graph_1
def graph_1(city_id):

    price_list = []
    sqft_list = []

    #Grab price and sqft data from DB
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Price, SQFT "
    statement += "FROM Apartments "
    statement += "WHERE City = '{}'".format(city_id)
    cur.execute(statement)
    for i in cur:
        price_list.append(i[0])
        sqft_list.append(i[1])
    conn.close()

    #Grab city name from DB
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Name, State "
    statement += "FROM Cities "
    statement += "WHERE Id = '{}'".format(city_id)
    cur.execute(statement)
    x = cur.fetchall()
    city_name = x[0][0]
    state_name = x[0][1]
    conn.close()

    # Create a trace
    trace = go.Scatter(
        x = price_list,
        y = sqft_list,
        mode = 'markers',
        marker = dict(
                size = 14,
                color = "rgb(67, 164, 20)"
        )
    )

    layout = dict(
            title = "<b>Rent & Square Footage of Apartments in {}, {}</b>".format(city_name, state_name),
                    titlefont=dict(
                                size=20
                            ),
            xaxis = dict(
                    title = '<b>Rent</b>',
                    titlefont=dict(
                                size=18
                            )
            ),
            yaxis = dict(
                    title = '<b>Square Feet</b>',
                    titlefont=dict(
                                size=18
                            )
            )
    )

    data = [trace]

    fig = dict(data=data, layout=layout)

    #plot
    # plot_url = py.plot(data, filename='basic-line')
    py.plot(fig, filename="Rent SQFT Apts {}".format(city_name))
#end of graph_1

#start of graph_2
def graph_2(city_id):

    price_list = []
    sqft_list = []

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Price, SQFT "
    statement += "FROM Apartments "
    statement += "WHERE City = '{}'".format(city_id)
    cur.execute(statement)
    for i in cur:
        price_list.append(i[0])
        sqft_list.append(i[1])
    conn.close()

    #Grab city name from DB
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Name, State "
    statement += "FROM Cities "
    statement += "WHERE Id = '{}'".format(city_id)
    cur.execute(statement)
    x = cur.fetchall()
    city_name = x[0][0]
    state_name = x[0][1]
    conn.close()

    # Create a trace
    trace0 = go.Box(
    y = price_list,
    name = '<b>Rent</b>',
    marker = dict(
        color = "rgb(67, 164, 20)",
    )
    )
    trace1 = go.Box(
    y = sqft_list,
    name = '<b>Square Feet</b>',
    marker = dict(
        color = "rgb(248, 92, 54)",
    )
    )

    data = [trace0, trace1]

    layout = dict (
    title = "<b>Box Plots for Rent & Square Footage in {}, {}</b>".format(city_name, state_name),
    titlefont=dict(
                size=20
            )
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename="Box Plots Rent SQFT {}".format(city_name))
#end of graph_2

def graph_3():
    pass

def graph_4():
    pass


if __name__ == "__main__":
    while True:
        # user_input = input('Please enter a U.S. city and state abbreviation\ne.g. "philadelphia-pa" ')
        user_input = input('Please enter a command\ne.g. "city_insert" ')

        if user_input.lower() == 'exit':
            break

        #to be consolidated later as 'start up' funct
        elif user_input.lower() == 'db_setup':
            db_setup(DBNAME)

        elif user_input.lower() == 'city_insert':
            while True:
                city_input = input('Enter your first city in format {City Name}-{State Abbrev}: ')
                if '-' in city_input:
                    city = city_input.split('-')[0]
                    state = city_input.split('-')[1]
                    find = cities_id(city,state) #holds the id of the relevant Cities record in DB
                    apartment_prices(city_input,find)
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

                if graph1_input.lower() == 'exit':
                    break

        elif user_input.lower() == 'graph_2':
            while True:
                graph2_input = input('Which city would you like to plot?\nPlease enter in format {City Name}-{State Abbrev}: ')
                if '-' in graph2_input:
                    city = graph2_input.split('-')[0]
                    state = graph2_input.split('-')[1]
                    # try:
                    #     conn = sqlite3.connect(DBNAME)
                    #     cur = conn.cursor()
                    #     statement = "SELECT Id from Cities WHERE Name='{}' and State = '{}'".format(city.title(),state.upper())
                    #     cur.execute(statement)
                    #     x = cur.fetchall()
                    #     city_id = x[0][0]
                    #     graph_2(city_id)
                    # except Exception as e:
                    #     print("Error querying DB: ",e)
                    #     conn.close()
                    conn = sqlite3.connect(DBNAME)
                    cur = conn.cursor()
                    statement = "SELECT Id from Cities WHERE Name='{}' and State = '{}'".format(city.title(),state.upper())
                    cur.execute(statement)
                    x = cur.fetchall()
                    city_id = x[0][0]
                    graph_2(city_id)
                    conn.close()

                if graph2_input.lower() == 'exit':
                    break
