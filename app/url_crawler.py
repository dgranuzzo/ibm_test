#coding: utf-8

import requests
from bs4 import BeautifulSoup

from messages import  * 

HTTPS_PREFIX = "https://"
HTTP_PREFIX = "http://"
HTTP = "http"

class CrawlerMachine:
    def __init__(self):
        """
        Conectar ao Mysql
        Args:
            config: {'server', 'database', 'user', 'password'}
        """        
        # using set to avoid duplicates
        self.urls_set = set()


    def find_urls(self,search_url):
        '''
        receives the search url and returns a dict with 
        the status and a list with the urls found
        '''
        # reinitialize the set
        self.urls_set = set()

        # verify if user inserted http:// or https:// in url
        if HTTPS_PREFIX in search_url:
            #ok, pass
            pass
        elif HTTP_PREFIX in search_url:
            #ok, pass
            pass
        else:
            # insert https:// to avoid invalid schema error
            # it does not correct if the user types http:\\ 
            search_url = HTTPS_PREFIX + search_url

        print(search_url)
        try:
            response = requests.get(search_url)
        except Exception as e:
            print(str(e))
            if str(e).startswith("Invalid URL"):
                return {"status":400,"message":MSG_INVALID_URL,"urls_set":self.urls_set}
            else:
                return {"status":400,"message":MSG_SERVICE_UNAVAILABLE,"urls_set":self.urls_set}

        status = response.status_code
        if response.status_code == 200:
            bs = BeautifulSoup(response.text, 'html.parser')

            for link in bs.find_all('a'):
                if 'href' in link.attrs:
                    self.urls_set.add(link.attrs['href'])

            message = MSG_OK

        elif response.status_code == 403:
            message = MSG_FORBIDEN

        return {"status":status,"message":message,"urls_set":self.urls_set}
