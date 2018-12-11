#507 final project
import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
import random

#start of funct to load text from file
def load_help_text():
    with open('help.txt') as f:
        return f.read()
#end of funct to load text from file

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
        if beds == "":
            self.beds = None
        else:
            self.beds = beds
        if baths == "":
            self.baths = None
        else:
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
        'URL' TEXT UNIQUE,
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

#start of funct to check if city is in DB
def check_city(city,state):
    city_id = 0
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Id from Cities WHERE Name='{}' and State = '{}'".format(city.title(),state.upper())
    cur.execute(statement)
    x = cur.fetchall()
    city_id = x[0][0]

    return city_id
    conn.close()
#end of funct to check if city is in DB

#start of funct to pull random city id
def rando_city():
    existing_cities = []
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = "SELECT Id from Cities"
    cur.execute(statement)
    for i in cur:
        existing_cities.append(i)
    conn.close()
    x = random.choice(existing_cities)
    return x[0]
#end of funct to pull random city id

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
        # print("Retrieving from cache...")
        return CACHE_DICT[url]
    else:
        # print("Retrieving from site...")
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

    #crawl up to 20 pages at Zillow.com
    for i in range(0,20):
        try:
            page = i+1

            zil_base_url = 'https://www.zillow.com/homes/for_rent'
            zil_city_url = zil_base_url+"/"+city+"/"+str(page)+"_p"
            # print('URL to crawl: ',zil_city_url)
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
                            zil_beds_clean = zil_beds.replace("-","")
                    except:
                        pass

                #FINDING BATHS
                zil_bathsX = home_soup.find(class_ = "zsg-content-header addr")
                zil_bathsY = zil_bathsX.find_all(class_="addr_bbs")
                for i in zil_bathsY:
                    if 'bath' in i.text:
                        zil_bathsZ = i.text.split(' ')[0]
                        zil_bathsZ_clean = zil_bathsZ.replace("-","")
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

                x = ZillowHome(streetAddress = zil_streetAddress_cleaner, city = city_id, price = zil_price_clean, beds = zil_beds_clean, baths = zil_bathsZ_clean, sqft = zil_sqftZ_clean, url = zil_url)
                # print(x)
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

#start of graph_3 - stacked bar chart using rent
def graph_3(city_idA, city_idB):

    price_listA = []
    price_listB = []

    # category = [counta, countb]
    price_0_800 = [0,0]
    price_801_1000 = [0,0]
    price_1001_1500 = [0,0]
    price_1501_2000 = [0,0]
    price_2001 = [0,0]

    # rent for cityA
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Price "
        statement += "FROM Apartments "
        statement += "WHERE City = '{}'".format(city_idA)
        cur.execute(statement)
        for i in cur:
            price_listA.append(i[0])
        conn.close()
    except Exception as e:
        print('Issue getting rent from DB.',e)
    # rent for cityA

    # rent for cityB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Price "
        statement += "FROM Apartments "
        statement += "WHERE City = '{}'".format(city_idB)
        cur.execute(statement)
        for i in cur:
            price_listB.append(i[0])
        conn.close()
    except Exception as e:
        print('Issue getting rent from DB.',e)
    # rent for cityB

    #iterate through rent prices for city A & tally up counts in rent categories
    for i in price_listA:
        if i <= 800:
            price_0_800[0] += 1
        elif (i > 800 and i <= 1000):
            price_801_1000[0] += 1
        elif (i > 1000 and i <= 1500):
            price_1001_1500[0] += 1
        elif (i > 1500 and i <= 2000):
            price_1501_2000[0] += 1
        elif (i > 2000):
            price_2001[0] += 1
    #iterate through rent prices for city A & tally up counts in rent categories

    #iterate through rent prices for city B & tally up counts in rent categories
    for i in price_listB:
        if i <= 800:
            price_0_800[1] += 1
        elif (i > 800 and i <= 1000):
            price_801_1000[1] += 1
        elif (i > 1000 and i <= 1500):
            price_1001_1500[1] += 1
        elif (i > 1500 and i <= 2000):
            price_1501_2000[1] += 1
        elif (i > 2000):
            price_2001[1] += 1
    #iterate through rent prices for city B & tally up counts in rent categories

    #Grab cityA name from DB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Name, State "
        statement += "FROM Cities "
        statement += "WHERE Id = '{}'".format(city_idA)
        cur.execute(statement)
        x = cur.fetchall()
        city_nameA = x[0][0]
        state_nameA = x[0][1]
        conn.close()
    except Exception as e:
        print('Issue finding city in DB.',e)
    #Grab cityA name from DB

    cityA_str = city_nameA+', '+state_nameA

    #Grab cityB name from DB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Name, State "
        statement += "FROM Cities "
        statement += "WHERE Id = '{}'".format(city_idB)
        cur.execute(statement)
        x = cur.fetchall()
        city_nameB = x[0][0]
        state_nameB = x[0][1]
        conn.close()
    except Exception as e:
        print('Issue finding city in DB.',e)
    #Grab cityB name from DB

    cityB_str = city_nameB+', '+state_nameB

    #trace1
    trace1 = go.Bar(
    x = [cityA_str, cityB_str],
    y = [price_0_800[0],price_0_800[1]],
    marker=dict(
        color='rgb(67, 164, 20)'),
    name = '<=800'
    )

    #trace2
    trace2 = go.Bar(
    x = [cityA_str, cityB_str],
    y = [price_801_1000[0],price_801_1000[1]],
    marker=dict(
        color='rgb(0, 172, 234)'),
    name = '801 to 1000'
    )

    #trace3
    trace3 = go.Bar(
    x = [cityA_str, cityB_str],
    y = [price_1001_1500[0],price_1001_1500[1]],
    marker=dict(
        color='rgb(179, 112, 247)'),
    name = '1000 to 1500'
    )

    #trace4
    trace4 = go.Bar(
    x = [cityA_str, cityB_str],
    y = [price_1501_2000[0],price_1501_2000[1]],
    marker=dict(
        color='rgb(248, 92, 54)'),
    name = '1501 to 2000'
    )

    #trace5
    trace5 = go.Bar(
    x = [cityA_str, cityB_str],
    y = [price_2001[0],price_2001[1]],
    marker=dict(
        color='rgb(0,0,0)'),
    name = '2000+'
    )

    data = [trace1, trace2, trace3, trace4, trace5]
    layout = go.Layout(
            barmode='stack',
            title = "<b>Stacked Bars for Rent in {} & {}</b>".format(cityA_str, cityB_str),
            titlefont=dict(
                        size=20
                    )
            )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Stacked Bars {}-{}'.format(cityA_str, cityB_str))
#end of graph_3

#start of graph_4
def graph_4(city_idA, city_idB):

    # AVGs for cityA
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT AVG(Price), AVG(Beds), AVG(Baths), AVG(SQFT) "
        statement += "FROM Apartments "
        statement += "WHERE City = '{}'".format(city_idA)
        cur.execute(statement)
        x = cur.fetchall()
        avg_price_nameA = round(x[0][0],2)
        avg_beds_nameA = round(x[0][1],1)
        avg_baths_nameA = round(x[0][2],1)
        avg_sqft_nameA = round(x[0][3],2)
        conn.close()
    except Exception as e:
        print('Issue getting rent from DB.',e)
    # AVGs for cityA

    # AVGs for cityB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT AVG(Price), AVG(Beds), AVG(Baths), AVG(SQFT) "
        statement += "FROM Apartments "
        statement += "WHERE City = '{}'".format(city_idB)
        cur.execute(statement)
        x = cur.fetchall()
        avg_price_nameB = round(x[0][0],2)
        avg_beds_nameB = round(x[0][1],1)
        avg_baths_nameB = round(x[0][2],1)
        avg_sqft_nameB = round(x[0][3],2)
        conn.close()
    except Exception as e:
        print('Issue getting rent from DB.',e)
    # AVGs for cityB

    #Grab cityA name from DB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Name, State "
        statement += "FROM Cities "
        statement += "WHERE Id = '{}'".format(city_idA)
        cur.execute(statement)
        x = cur.fetchall()
        city_nameA = x[0][0]
        state_nameA = x[0][1]
        conn.close()
    except Exception as e:
        print('Issue finding city in DB.',e)
    #Grab cityA name from DB

    cityA_str = city_nameA+', '+state_nameA

    #Grab cityB name from DB
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Name, State "
        statement += "FROM Cities "
        statement += "WHERE Id = '{}'".format(city_idB)
        cur.execute(statement)
        x = cur.fetchall()
        city_nameB = x[0][0]
        state_nameB = x[0][1]
        conn.close()
    except Exception as e:
        print('Issue finding city in DB.',e)
    #Grab cityB name from DB

    cityB_str = city_nameB+', '+state_nameB

    diff_price = round(abs(avg_price_nameA-avg_price_nameB),2)
    diff_beds = round(abs(avg_beds_nameA-avg_beds_nameB),1)
    diff_baths = round(abs(avg_baths_nameA-avg_baths_nameB),1)
    diff_sqft = round(abs(avg_sqft_nameA-avg_sqft_nameB),2)

    trace = go.Table(
     header=dict(values=['City', 'Average Rent', 'Average # Beds', 'Average # Baths', 'Average SQFT'],
                line = dict(color='#7D7F80'),
                fill = dict(color='rgb(0, 172, 234)'),
                font = dict(color='white',size=12),
                # align = ['left'] * 1),
                align = ['left']),
    cells=dict(values=[[cityA_str,cityB_str, 'differences'], #col for city name
                       [avg_price_nameA, avg_price_nameB, diff_price],
                       [avg_beds_nameA, avg_beds_nameB, diff_beds],
                       [avg_baths_nameA, avg_baths_nameB, diff_baths],
                       [avg_sqft_nameA, avg_sqft_nameB, diff_sqft],
                       ],
               line = dict(color='#7D7F80'),
               fill = dict(color='#EDFAFF'),
               font = dict(color='black',size=12),
               # align = ['left'] * 1)
               align = ['left'])
               )

    layout = dict(
    autosize=False,
    title='<b>Apartment Averages for {} & {}</b>'.format(cityA_str, cityB_str),
    )
    data = [trace]
    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = 'AVG Apts {}-{}'.format(cityA_str, cityB_str))
#end of graph_4

if __name__ == "__main__":

    while True:
        #load help text
        try:
            help_text = load_help_text()
        except Exception as e:
            print('Issue loading help.txt. Check file is available.',e)
        #load help text

        #load details on cities in DB
        try:
            cities_avail = []
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement = "SELECT Cities.Name, Cities.State, Count(*) "
            statement += "FROM Apartments "
            statement += "LEFT JOIN Cities on Apartments.City == Cities.Id "
            statement += "GROUP BY City "
            statement += "ORDER BY Cities.Name"
            cur.execute(statement)
            for i in cur:
                cities_avail.append(i)
            conn.close()
        except Exception as e:
            print('Issue loading cities from DB',e)
        #load details on cities in DB

        #start up greeting
        print('\nWELCOME TO CITY PROSPECTS: Review rental details for U.S. Cities\n\n')
        print('Available cities\n----------------')
        for i in cities_avail:
            print('{}-{} ({})'.format(i[0],i[1],i[2]))
        main_input = input("\nPlease enter a command (or 'help' for options): ")
        #start up greeting

        #input to return to previous screen or exit program
        if main_input.lower() == 'exit':
            break
        #input to return to previous screen or exit program

        #input to access help
        if main_input.lower() == 'help':
            while True:
                help_input = input(help_text)
                if help_input.lower() == 'exit':
                    break
        #input to access help

        #input to delete & rebuild DB
        if main_input.lower() == 'delete_db':
            while True:
                delete_input = input('Confirm you want to delete & rebuild the DB by typing "DELETE"\n\n')
                if delete_input == 'DELETE':
                    # print('gonna delete')
                    db_setup(DBNAME)
                    break
                elif delete_input.lower() == 'exit':
                    break
                elif delete_input.lower() == 'help':
                    while True:
                        help_print = input(help_text)
                        if help_print.lower() == 'exit':
                            break
        #input to delete & rebuild DB

        #input to add new city from Zillow
        if main_input.lower() == 'add city':
            while True:
                city_input = input('\nEnter a new city below in the format {city name}-{state abbrev}\nNOTE: crawling & scraping Zillow.com takes several minutes\n\n')
                if '-' in city_input:
                    city = city_input.split('-')[0]
                    state = city_input.split('-')[1]
                    find = cities_id(city,state) #holds the id of the relevant Cities record in DB
                    apartment_prices(city_input,find)
                elif city_input.lower() == 'exit':
                    break
                elif city_input.lower() == 'help':
                    while True:
                        help_print = input(help_text)
                        if help_print.lower() == 'exit':
                            break
        #input to add new city from Zillow

        #input to visualize data on apts
        if main_input.lower() == 'visuals':
            while True:
                visuals_input = input('\nSelect a visualization:\n1 - scatter plot of rent & square feet for a city\n2 - box plots of rent & square feet for a city\n3 - stacked bars comparing rent in 2 cities\n4 - table of averages comparing 2 cities\n\n')

                #generate scatter or box plot of rent & SQFT for selected city
                if (visuals_input.lower() == '1' or visuals_input.lower() == '2') :
                        while True:
                            graph_input = input('Which city would you like to plot?\nPlease enter in format {city name}-{state abbrev}\n\n')

                            if '-' in graph_input:
                                city = graph_input.split('-')[0]
                                state = graph_input.split('-')[1]
                                try:
                                    # conn = sqlite3.connect(DBNAME)
                                    # cur = conn.cursor()
                                    # statement = "SELECT Id from Cities WHERE Name='{}' and State = '{}'".format(city.title(),state.upper())
                                    # cur.execute(statement)
                                    # x = cur.fetchall()
                                    # city_id = x[0][0]
                                    city_id = check_city(city,state)

                                    if visuals_input == '1':
                                        graph_1(city_id)
                                    elif visuals_input == '2':
                                        graph_2(city_id)
                                except:
                                    print("\nCould not visualize '{}'. Please try adding a city from main menu or try an available city.\n".format(graph_input))
                                    # conn.close()

                            #input to return to previous screen or exit program
                            if graph_input.lower() == 'exit':
                                break

                            #input to access help
                            if graph_input.lower() == 'help':
                                while True:
                                    help_print = input(help_text)
                                    if help_print.lower() == 'exit':
                                        break
                            #input to access help
                #generate scatter or box plot of rent & SQFT for selected city

                #generate stacked bar chart using rent or summary table comparing cities
                if (visuals_input.lower() == '3' or visuals_input.lower() == '4') :
                    while True:
                        #start funct to find cityA
                        graph_inputA = input('\nEnter your 1st city in format {city name}-{state abbrev} or try "random".\n\n')
                        if graph_inputA == 'exit':
                            break
                        if '-' in graph_inputA:
                            city = graph_inputA.split('-')[0]
                            state = graph_inputA.split('-')[1]
                            try:
                                city_idA = check_city(city,state)
                            except Exception as e:
                                print("\nCould not find '{}'. Please try adding a city from main menu or try an available city.\n".format(graph_inputA))
                                conn.close()
                                break
                        if graph_inputA == "random":
                            city_idA = rando_city()
                        if '-' not in graph_inputA:
                            print("\nCould not find '{}'. Please try adding a city from main menu or try an available city.\n".format(graph_inputA))
                            break
                        #end funct to find cityA

                        #start funct to find cityB
                        graph_inputB = input('\nEnter your 2nd city in format {city name}-{state abbrev} or try "random".\n\n')
                        if graph_inputB == 'exit':
                            break
                        if '-' in graph_inputB:
                            city = graph_inputB.split('-')[0]
                            state = graph_inputB.split('-')[1]
                            try:
                                city_idB = check_city(city,state)
                            except Exception as e:
                                print("\nCould not find '{}'. Please try adding a city from main menu or try an available city.\n".format(graph_inputB))
                                conn.close()
                                break
                        if graph_inputB == "random":
                            city_idB = rando_city()
                        if '-' not in graph_inputB:
                            print("\nCould not find '{}'. Please try adding a city from main menu or try an available city.\n".format(graph_inputB))
                            break
                        #end funct to find cityB

                        try:
                            if visuals_input == '3':
                                graph_3(city_idA, city_idB)
                            elif visuals_input == '4':
                                graph_4(city_idA, city_idB)
                        except Exception as e:
                            print("\nCould not visualize '{}' and/or '{}'. Please try adding cities from main menu or try available cities.\n".format(graph_inputA, graph_inputB))

                #generate stacked bar chart using rent or summary table comparing cities

                elif visuals_input.lower() == 'exit':
                    break
                elif visuals_input.lower() == 'help':
                    while True:
                        help_print = input(help_text)
                        if help_print.lower() == 'exit':
                            break
        #input to visualize data on apts
