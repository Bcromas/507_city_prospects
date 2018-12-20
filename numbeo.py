#Numbeo API funct
from secret import numbeo_key
from city_prospects import *
import requests
import json

base_url = 'https://www.numbeo.com/api/'

#start Numbeo caching functionality
CACHE_FNAME = 'numbeo_CACHE.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICT = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICT = {}
#end Numbeo caching functionality

#start of simple check of cache
def check_numbeo_cache(url):

    if url in CACHE_DICT:
        print("Retrieving from cache...")
        return CACHE_DICT[url]
    else:
        print("Retrieving from site...")
        resp = requests.get(url)
        CACHE_DICT[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICT)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICT[url]
#end of simple check of cache

#start of funct to get primary transit means for given city from Numbeo
def transit_means(city, state, city_id):

    traffic_url = 'city_traffic?api_key={}&query={}'.format(numbeo_key,city,'%20',state)

    #start of grabbing & assigning results to 'primary_means' var
    try:
        test = check_numbeo_cache(base_url+traffic_url)
        loaded_text = json.loads(test)
        percent_walking = round(loaded_text['primary_means_percentage_map']['Walking'],2)
        percent_train_metro = round(loaded_text['primary_means_percentage_map']['Train/Metro'],2)
        percent_car = round(loaded_text['primary_means_percentage_map']['Car'],2)
        percent_WFH = round(loaded_text['primary_means_percentage_map']['Working from Home'],2)
        percent_bus = round(loaded_text['primary_means_percentage_map']['Bus/Trolleybus'],2)
        percent_tram = round(loaded_text['primary_means_percentage_map']['Tram/Streetcar'],2)
        percent_other = round(100-percent_walking-percent_train_metro-percent_car-percent_WFH-percent_bus-percent_tram,2)
    except Exception as e:
        print('Issue getting primary transit means from Numbeo',e)
    #end of grabbing & assigning results to 'primary_means' var

    #start of connecting to DB & updating existing Cities record with primary transit means
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = 'UPDATE Cities '
        statement += "SET 'Primary Transit: Walking' = {},'Primary Transit: Train' = {},'Primary Transit: Car' = {},'Primary Transit: WFH' = {},'Primary Transit: Bus' = {},'Primary Transit: Tram' = {},'Primary Transit: Other' = {} ".format(percent_walking, percent_train_metro, percent_car, percent_WFH, percent_bus, percent_tram, percent_other)
        statement += 'WHERE Id = {}'.format(city_id)
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print('Issue writing transit means to DB',e)
    #end of connecting to DB & updating existing Cities record with primary transit means
#end of funct to get primary transit means for given city from Numbeo

#start of funct to get cost of living estimate for given city from Numbeo
def Numbeo_indices(city, state, city_id):

    indices_url = 'indices?api_key={}&query={}{}{}'.format(numbeo_key, city,'%20',state)

    # test = check_numbeo_cache(base_url+indices_url)
    # print(test)

    try:
        test = check_numbeo_cache(base_url+indices_url)
        loaded_text = json.loads(test)

        try:
            qol_index = round(loaded_text['quality_of_life_index'],2)
        except:
            qol_index = None
        try:
            cpi_index = round(loaded_text['cpi_index'],2)
        except:
            cpi_index = None
        try:
            groceries_index = round(loaded_text['groceries_index'],2)
        except:
            groceries_index = None
        try:
            restaurant_price_index = round(loaded_text['restaurant_price_index'],2)
        except:
            restaurant_price_index = None
        try:
            crime_index = round(loaded_text['crime_index'],2)
        except:
            crime_index = None
        try:
            safety_index = round(loaded_text['safety_index'],2)
        except:
            safety_index = None
        try:
            traffic_index = round(loaded_text['traffic_index'],2)
        except:
            traffic_index = None
        try:
            traffic_time_index = round(loaded_text['traffic_time_index'],2)
        except:
            traffic_time_index = None
        try:
            traffic_inefficiency_index = round(loaded_text['traffic_inefficiency_index'],2)
        except:
            traffic_inefficiency_index = None
        try:
            health_care_index = round(loaded_text['health_care_index'],2)
        except:
            health_care_index = None
        try:
            pollution_index = round(loaded_text['pollution_index'],2)
        except:
            pollution_index = None
        try:
            climate_index = round(loaded_text['climate_index'],2)
        except:
            climate_index = None
    except Exception as e:
        print('Issue getting indices from Numbeo',e)

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = 'UPDATE Cities '
        statement += "SET 'Quality of Life Index' = '{}','CPI Index' = '{}','Groceries Index' = '{}','Restaurant Price Index' = '{}','Crime Index' = '{}','Safety Index' = '{}','Traffic Index' = '{}', 'Traffic Time Index' = '{}', 'Traffic Inefficiency Index' = '{}', 'Health Care Index' = '{}', 'Climate Index' = '{}', 'Pollution Index' = '{}' ".format(qol_index, cpi_index, groceries_index, restaurant_price_index, crime_index, safety_index, traffic_index, traffic_time_index, traffic_inefficiency_index, health_care_index, climate_index, pollution_index)
        statement += 'WHERE Id = {}'.format(city_id)
        # print(statement)
        cur.execute(statement)
        conn.commit()
    except Exception as e:
        print("Issue writing Numbeo indices to DB",e)
#end of funct to get cost of living estimate for given city from Numbeo
