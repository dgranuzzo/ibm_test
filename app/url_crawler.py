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
        creates the instance

        """        
        # using set to avoid duplicates
        self.urls_set = set()
        self.initial_url = ""


    def find_urls(self,search_url):
        '''
        receives the search url and returns a dict with 
        the status and a list with the urls found
        '''
        # reinitialize the set
        self.urls_set = set()
        message = "initialized"

        search_url = str(search_url).strip()
        if not search_url.startswith(HTTP):
            # nsert "http://" to avoid scheme error 
            search_url = "http://" + search_url

        print(search_url)
        try:
            # request in the search url:
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
                    new_url = link.attrs['href']
                    new_url = self.clean_url(new_url,search_url)
                    if new_url == DO_NOT_INCLUDE_URL:
                        # dont include this one!!!
                        pass
                    else:
                        self.urls_set.add(new_url)
            message = MSG_OK
        elif response.status_code == 403:
            message = MSG_FORBIDEN
        else:
            message = "unknown error"

        return {"status":status,"message":message,"urls_set":self.urls_set}


    def clean_url(self,new_url,search_url=""):
        """
        Treat the new_url to remove undesireble text. Returns the new_url sanitized.
        (remove get variables from url (text after ?) , include https:// when needed, 
        include initial_url when url starts with "/")

        Args: new_url (str) , search_url(str)


        Returns: new_url (str)

        """
        new_url = new_url.strip()
        print(new_url)
        if len(new_url)> 3 and "///" not in "new_url":
            # if "?"" in url, remove text from "?", including it
            
            if "#" in new_url:
                new_url = new_url.split("#")[0]
            elif "?" in new_url:
                new_url = new_url.split("?")[0]

            # if new_url starts with / , includes https://serach_urlnew_url
            # check len again, after possible len reduction above
            if len(new_url)> 3:
                if new_url.startswith("http"):
                    pass
                elif new_url[0] == "/":
                    new_url = HTTPS_PREFIX + search_url + new_url
                else:
                    new_url = HTTP_PREFIX + new_url
            else:
                new_url = DO_NOT_INCLUDE_URL    
        else:
            new_url = DO_NOT_INCLUDE_URL

        return new_url
