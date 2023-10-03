import requests
import os
import json
import time
import sys
from chillie_util import setLogger, pooh_header, picker_header
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import ACTION_TYPE_LIKE, ACTION_TYPE_RETWEET, ACTION_TYPE_QUOTE, ACTION_TYPE_REPLY, db_insert_pooh_like, db_insert_pooh_retweet, db_is_pooh_existing

# Python Script to add a user to BlackList if they fell for a HoneyPot by liking tweet
#       When they were told NOT to like the Tweet.
setLogger("log_chillie_sniffer.log")


running_total = 0

#TODO: Track the amount of Remaining Requests are available!

def create_url_likes_and_retweets(action_type, host_post_id):
    # Whats the URL we want to Sniff?
    if action_type == ACTION_TYPE_LIKE:
        return "https://api.twitter.com/2/tweets/{}/liking_users".format(host_post_id)
    if action_type == ACTION_TYPE_RETWEET:
        return "https://api.twitter.com/2/tweets/{}/retweeted_by".format(host_post_id)
    return None


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
    
def connect_to_endpoint(url, next_token):
    print("ChilliePicker is still hungry!!")

    if next_token == None:
        queries = {'max_results': 100}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    else:
        queries = {'pagination_token': next_token, 'max_results': 100}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
        
    # TODO - CHILLIEMAN - Check the response.header for remaining Calls - If it is 0 - WAIT the next time you arrive in this function
    
    if response.status_code == 429:
        # TODO - Remove the need for this!! You should never be getting this Error because you should know when wait by looking at HTTP Headers
        # Wait for 15 minutes, then return the same token
        print("ChilliePicker is too fat for Twitter - Must Take a nap!")
        snooze()
        return connect_to_endpoint(url, next_token)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

    # user properties of Interest: 
    # "id" - Unique ID
    # "name" - Profile Name
    # "username" - @UserName
    
    # NONDEFAULTS:
    # ?user.fields=verified,public_metrics
    # "verified" - Blue Check Status
    # "public_metrics"
    #      "followers_count"
    #      "following_count"
    
def process_likes_and_retweets(action_type, host_post_id, users):
    for u in users:
        username = u['username']
        profile_name = u['name']
        twitter_id = u['id']
        if db_is_pooh_existing(action_type, twitter_id, host_post_id, username):
            print("Ive already had this Honey")
        else:
            if action_type == ACTION_TYPE_LIKE:
                db_insert_pooh_like(twitter_id, username, profile_name, host_post_id)
            if action_type == ACTION_TYPE_RETWEET:
                db_insert_pooh_retweet(twitter_id, username, profile_name, host_post_id)
               

def get_next_token(request):
    try:
        return request['meta']['next_token']
    except KeyError as ke:
        return None

def naughty(action_type, host_tweet_id, json_response):
    pooh_header(["Honey??"], '/', False)
    time.sleep(1)
    #Naughty Naughty!!
    try:
        users = json_response['data']
        for u in users:
            print("Naughty Naughty! --> @{}".format(u['username']))
        pooh_header(["Imma Eatum"], '!', False)
        time.sleep(2)
        process_likes_and_retweets(action_type, host_tweet_id, users)
    except KeyError as err:
        pooh_header(["Yummy!"], '!', False)
        time.sleep(2)
        
    try:
        return json_response['meta']['result_count']
    except KeyError as err:
        return 0
        
        
def sniff_likes_and_retweets(action_type, token, host_tweet_id):
    url = create_url_likes_and_retweets(action_type, host_tweet_id)
    
    json_response = connect_to_endpoint(url, token)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    global running_total
    running_total += naughty(action_type, host_tweet_id, json_response)
    return get_next_token(json_response)

def is_action_type_valid(text):
    if text == ACTION_TYPE_LIKE or text == ACTION_TYPE_RETWEET or text == ACTION_TYPE_REPLY or text == ACTION_TYPE_QUOTE:
        return True
    return False
    
def main():
    if len(sys.argv) != 3:
        raise Exception("You must provide ACTION_TYPE, then Host Tweet ID")
    
    # Arguments passed
    action_type = sys.argv[1].upper()
    post_id = sys.argv[2]
    
    if not is_action_type_valid(action_type):
        raise Exception("Bad Action Type: {}".format(action_type))

    
    picker_header(["Hello Chillieman!", "Lets Check for {} on...".format(action_type), post_id ], '*', False)
    time.sleep(1)
    next_token = sniff_likes_and_retweets(action_type, None, post_id)
    while next_token != None:
        next_token = sniff_likes_and_retweets(action_type, next_token, post_id)
    else:
        message = ["Pooh is satisfied -", "There are {} Naughty Mfers!!".format(running_total)]
        picker_header(message, '*', False)

if __name__ == "__main__":
    main()
