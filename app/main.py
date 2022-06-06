import uvicorn
from fastapi import HTTPException, status
#from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks,FastAPI
import os
from dotenv import load_dotenv

from url_crawler import CrawlerMachine
from sql_app import MysqlDb
import re
from messages import  * 

load_dotenv()
app = FastAPI()

RECURRENCE_LIMIT = 200
HTTPS_PREFIX = "https://"

CrawlerMach = CrawlerMachine()

# any service can reach any other service at that service’s name. 
# In the following example, db is reachable from web at the hostnames db
config = {
        'server': os.getenv('server'), 
        'database': os.getenv('database'), 
        'user': os.getenv('user'), 
        'password': os.getenv('password'),
        'port': "3306",
        }

print(config)
SqlDB = MysqlDb(config)

def recurring_call(urls_set,results,count):
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
                new_urls_set = new_urls_set.union(dict_return['urls_set'])
                # after that url is searched for new urls, its appended to results
            results.append(url)
            
            print("count: {} , urls_set: {}".format(count,len(urls_set)))
            print('going for next recurring call: {}'.format(RECURRENCE_LIMIT))

            # exclude urls found in other pages to avoid duplicates
            only_new_urls_set = new_urls_set.difference(urls_set)
            print(only_new_urls_set)

            count+=1
            # break for loop when count is greater than recurrence limit 
            if count > RECURRENCE_LIMIT:
                break
            
            # when urls_set is over, call function again with new set of urls
            recurring_call(only_new_urls_set,results,count)
    
    # return when all urls were searched
    return results



def start_crawler(initial_url,urls_set):
    """
    Start the recurrent function to scrap the url

    Args: first set() of urls extracted of the url.

    Returns: None
    """
    count = 0
    results = []
    # recurring call
    urls_to_save_list = recurring_call(urls_set, results, count)

    # save in database array of values (initial_url, found_url)
    urls_to_save_tuples_list = []
    for url_item in urls_to_save_list:
        # array [(initial_url, found_url_1), (initial_url, found_url_2), ...]
        urls_to_save_tuples_list.append((initial_url,url_item))
    
    # print save in databse
    print("SAVE IN DATABASE:")
    print(urls_to_save_tuples_list)
    if len(urls_to_save_tuples_list) > 0:
        response = SqlDB.save_urls(urls_to_save_tuples_list)
        print(response)
    
    return 1
        
    
@app.post("/url")
async def post_url(url: str, background_tasks: BackgroundTasks):
    print(url)
    if not url:
        raise HTTPException(status_code=400, detail="Incorrect payload")
    else:
        try:
            dict_return = CrawlerMach.find_urls(url)
            urls_set = dict_return['urls_set']

            background_tasks.add_task(start_crawler,url,urls_set)
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


@app.get("/create_url_table")
def create_url_table():
    try:
        response = SqlDB.create_url_table()
    except Exception as e:
        response = {"status":str(e)}
    return response


if __name__=='__main__':
    print("init main")
    port=80
    print('listening on port {}'.format(port))
    uvicorn.run(app, host="0.0.0.0", port=port)


