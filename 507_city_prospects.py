#507 final project
#Compare housing costs, startup environment, and cost of living between three U.S. cities.
import requests
import json
from bs4 import BeautifulSoup

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

#object for capturing Zillow home details
class ZillowHome():
    def __init__(self, streetAddress, beds=None, baths=None, rooms=None, sqft=None, price=None, price_sqft=None, est_mortgage=None, url=None):
        self.streetAddress = streetAddress
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
def home_prices(city):
    zil_base_url = 'https://www.zillow.com/homes/for_sale'
    zil_city_url = zil_base_url+"/"+city
    city_in_cache = check_cache(zil_city_url)
    city_soup = BeautifulSoup(city_in_cache,'html.parser')
    photo_cards = city_soup.find(class_="photo-cards")
    # test_list = []
    for i in photo_cards:
        try:
            home_url = i.a['href']
            zil_home_url = zil_base_url+home_url
            home_in_cache = check_cache(zil_home_url)
            home_soup = BeautifulSoup(home_in_cache,'html.parser')
            zil_streetAddress = home_soup.find(class_="zsg-h1 hdp-home-header-st-addr").text
            x = ZillowHome(streetAddress=zil_streetAddress)
            test_list.append(x)
            #call ZillowHome with streetAddress, beds, baths, rooms, sqft, price, price_sqft, est_mortgage, url=None)

        except:
            pass

    for i in test_list: #continue adding attributes from home page to call to ZillowHome(), uncomment line 59,
        print(i)
#end of crawling Zillow for homes

if __name__ == "__main__":
    while True:
        user_input = input('Please enter a U.S. city and state abbreviation\ne.g. "philadelphia-pa" ')

        if user_input.lower() == 'exit':
            break

        else:
            home_prices(user_input)
            # zil_base_url = 'https://www.zillow.com/homes/for_sale/'
            # url = zil_base_url+user_input
            # url_in_cache = check_cache(url)
            # url_soup = BeautifulSoup(url_in_cache,'html.parser')
            # facts_table = url_soup.find(class_="zsg-table")
            # table_rows = facts_table.find_all('tr')
            # for i in table_rows:
            #     print(i.text)
            #     print("*"*20)


#http://api.wolframalpha.com/v2/query?appid=DEMO&input=population%20france&includepodid=Result&format=plaintext
#http://api.wolframalpha.com/v2/query?appid=RTT5K2-JEYKEW4HKK&input=cost%20of%20living%20boston
