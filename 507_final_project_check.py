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

if __name__ == "__main__":
    while True:
        user_input = input('Please enter a U.S. city and state abbreviation\ne.g. "philadelphia-pa" ')

        if user_input.lower() == 'exit':
            break

        else:
            base_url = 'https://www.zillow.com/homes/for_sale/'
            url = base_url+user_input
            url_in_cache = check_cache(url)
            url_soup = BeautifulSoup(url_in_cache,'html.parser')
            facts_table = url_soup.find(class_="zsg-table")
            table_rows = facts_table.find_all('tr')
            for i in table_rows:
                print(i.text)
                print("*"*20)
