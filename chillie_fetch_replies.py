import requests
import os
import json
import time
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import db_insert_tweet
from chillie_util import setLogger, picker_header

setLogger("log_fren_chillie_picker.log")

post_id = '1661157611012538368'
query_formatted = 'in_reply_to_tweet_id:{}'.format(post_id)
running_total = 0

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    r.headers["User-Agent"] = "ChilliePicker"
    return r

def snooze():
    print("ZZzz (15 Minutes Left)")
    time.sleep(60 * 10)
    print("Zz (5 Minutes Left)")
    time.sleep(60 * 4)
    print("Z (1 Minute Left)")
    time.sleep(60)
    print("*Yawn* I feel Recharged!!")
    
def connect_to_endpoint(next_token):
    url = "https://api.twitter.com/2/tweets/search/recent"

    if next_token == None:
        queries = {'query': query_formatted, 'expansions': 'author_id', 'max_results': 100}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    else:
        queries = {'query': query_formatted, 'pagination_token': next_token, 'expansions': 'author_id', 'max_results': 100 }
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
        
    
    if response.status_code == 429:
        # Wait for 15 minutes, then return the same token
        print("ChilliePicker is too fat for Twitter - Must Take a nap!")
        snooze()
        return connect_to_endpoint(next_token)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def process_replies(replies):
    for r in replies:
        text = r['text']
        author_id = r['author_id']
        #Check if post contains 0x OR .eth?
        db_insert_tweet(text, author_id)
        print(text)
            
def get_next_token(request):
    try:
        return request['meta']['next_token']
    except KeyError as ke:
        return None
        
def consume_replies(json_response):
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    try:
        replies = json_response['data']
        process_replies(replies)
    except KeyError as err:
        print("Thinking...")
        
    try:
        return json_response['meta']['result_count']
    except KeyError as err:
        return 0
        
def pull_tweets(token):    
    json_response = connect_to_endpoint(token)
    global running_total
    running_total += consume_replies(json_response)
    return get_next_token(json_response)
        
def main():
    picker_header(['Collecting AirDrop #2 List!'], '*', False)
    
    next_token = pull_tweets(None)
    while next_token != None:
        next_token = pull_tweets(next_token)
    else:
        message = ["I'm satisfied -", "{} Replies Scraped!!".format(running_total)]
        picker_header(message, '*', False)


if __name__ == "__main__":
    main()
