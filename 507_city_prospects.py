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

def home_prices(city):
    zil_base_url = 'https://www.zillow.com/homes/for_sale'
    zil_city_url = zil_base_url+"/"+city
    city_in_cache = check_cache(zil_city_url)
    city_soup = BeautifulSoup(city_in_cache,'html.parser')
    photo_cards = city_soup.find(class_="photo-cards")
    for i in photo_cards:
        try:
            home_url = i.a['href']
            zil_home_url = zil_base_url+home_url
            home_in_cache = check_cache(zil_home_url)
        except:
            pass

    #the lines below will find the summary table at the bottom of each page, need to
    # facts_table = url_soup.find(class_="zsg-table")
    # table_rows = facts_table.find_all('tr')
    # for i in table_rows:
    #     print(i.text)
    #     print("*"*20)

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
