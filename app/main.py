import uvicorn
from fastapi import HTTPException, status
#from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks,FastAPI
import os
from dotenv import load_dotenv

from url_crawler import CrawlerMachine
from sql_app import SqlDbClass
import re
from messages import  * 

load_dotenv()
app = FastAPI()

RECURRENCE_LIMIT = 20
HTTPS_PREFIX = "https://"

CrawlerMach = CrawlerMachine()

# any service can reach any other service at that service’s name. 
# In the following example, db is reachable from web at the hostnames db
config = {
        'server': os.getenv('server'), 
        'database': os.getenv('database'), 
        'user': os.getenv('user'), 
        'password': os.getenv('password'),
        'port': os.getenv('port'),
        }

print(config)
SqlDB = SqlDbClass(config)
resp = SqlDB.create_url_table()
print("create table:")
print(resp)

def recurring_call(initial_url, urls_set, results_set,count=0):
    """
    recurrent function to scrap the urls found. Limits the recurrence to LIMIT (950)

    Args: urls set() of urls found, counter.

    Returns: urls set() of urls found, counter.
    """
    # new set for this call of function
    
    new_urls_set = set()
    for url in urls_set:
        dict_return = CrawlerMach.find_urls(url)
        # include new results in new_urls_set
        if dict_return['message'] == MSG_OK:
            for url_item in dict_return['urls_set']:
                url_item = CrawlerMach.clean_url(url_item, url)
                
                if url_item not in results_set:
                    # add only if it is not in results_set yet
                    # results is cumulative
                    print("ADD URL: {}".format(url_item))
                    new_urls_set.add(url_item)
                    # after that url is searched for new urls, it is appended to results
                    results_set.add(url)
        
        print("====================================================")
        print("count: {} , urls_set: {}".format(count,len(urls_set)))
        
        count+=1
        
    # when urls_set is over, call function again with new set of urls
    print('check if going for next recurring call: {}'.format(RECURRENCE_LIMIT))
    if count < RECURRENCE_LIMIT:
        print("recurring call ...{}".format(count))
        recurring_call(initial_url, new_urls_set,results_set,count)



    print("THE RETURN RECURRING CALL ======")
    return results_set



def start_crawler(initial_url,urls_set):
    """
    Start the recurrent function to scrap the url

    Args: first set() of urls extracted of the url.

    Returns: None
    """
    print("1. start crawler =====")
    count = 0
    results_set = set()
    # recurring call
    urls_to_save_set = recurring_call(initial_url, urls_set, results_set, count)

    print("=== 2. urls to save tuple ===")
    # save in database array of values (initial_url, found_url)
    urls_to_save_tuples_list = []
    for url_item in urls_to_save_set:
        # array [(initial_url, found_url_1), (initial_url, found_url_2), ...]
        urls_to_save_tuples_list.append((initial_url,url_item))
    
    # print save in databse
    print("SAVE IN DATABASE:")
    print(urls_to_save_tuples_list)
    if len(urls_to_save_tuples_list) > 0:
        response = SqlDB.save_urls(urls_to_save_tuples_list)
        print(response)
    else:
        print("len problem: {}".format(len(urls_to_save_tuples_list)))
        
    
@app.post("/url")
async def post_url(url: str, background_tasks: BackgroundTasks):
    print(url)
    if not url:
        raise HTTPException(status_code=400, detail="Incorrect payload")
    else:
        try:
            dict_return = CrawlerMach.find_urls(url)
            urls_set = dict_return['urls_set']

            #background_tasks.add_task(start_crawler,url,urls_set)
            start_crawler(url,urls_set)
            print("**** return start_crawler: ****")
            print(dict_return)
            if dict_return['message'] == MSG_OK:
                urls_set = dict_return['urls_set']
                message = "First urls found in {}: {}".format(url,len(urls_set)) 
                status = dict_return['status']
            else:
                message = dict_return['message']
                status = dict_return['status']
        except Exception as e:
            print(e)
            message = MSG_SERVICE_UNAVAILABLE
            status = 577

    return {"message": message,"status":status}


@app.get("/url")
def get_url():
    return {"response": "send your url via post"}


@app.post("/url_results")
def get_url_results(url: str):
    results = SqlDB.get_urls(url)
    return {"results": results}

@app.get("/all_urls")
def get_url():
    all_data = SqlDB.get_all()
    return all_data


@app.get("/")
def read_root():
    return {"response": "try /url"}


@app.post("/test_urls_table")
def insert_url(initial_url: str,search_url:str):
    results = SqlDB.insert_into_urls(initial_url,search_url)
    return {"results": results}

if __name__=='__main__':
    print("init main")
    port=80
    print('listening on port {}'.format(port))
    uvicorn.run(app, host="0.0.0.0", port=port)


