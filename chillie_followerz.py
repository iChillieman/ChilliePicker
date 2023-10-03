import requests
import os
import json
import time
import sys
import random
import emoji
from chillie_util import setLogger, pooh_header, picker_header
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import db_insert_follower, db_insert_following, db_fetch_all_people_legend_is_following, db_is_following_by_twitter_id

setLogger("log_chillie_unfollowerz.log")

running_total = 0

legend_un = "IWantYouSP"

def create_url_pull_featured_account(username):    
    username_string = "usernames={}".format(username)
    url = "https://api.twitter.com/2/users/by?{}".format(username_string)
    return url
    
def create_url_followers_by_id(twitter_id):
    return "https://api.twitter.com/2/users/{}/followers".format(twitter_id)
    
def create_url_following_by_id(twitter_id):
    return "https://api.twitter.com/2/users/{}/following".format(twitter_id)

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

def connect_to_endpoint_fetch_user_by_username(username):
    url = create_url_pull_featured_account(username)
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
    
def connect_to_endpoint_followers_by_id(url, next_token):
    #Difference is we use a Max_Result as 1,000 - Instead of 100 when pulling Likes and Retweets.
    if next_token == None:
        queries = {'max_results': 1000}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    else:
        queries = {'pagination_token': next_token, 'max_results': 1000}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    
    if response.status_code == 429:
        # Wait for 15 minutes, then return the same token
        print("ChilliePicker is too fat for Twitter - Must Take a nap!")
        snooze()
        return connect_to_endpoint_followers_by_id(url, next_token)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
    

def process_followers(legend_id, legend_username, users):
    for u in users:
        follower_id = u['id']
        follower_username = u['username']
        #try:
        db_insert_follower(legend_id, legend_username, follower_id, follower_username)
        #except Exception as e:
        #    print("Seems this Follower already exists!!")

def process_following(legend_id, legend_username, users):
    for u in users:
        following_id = u['id']
        following_username = u['username']
        #try:
            # TODO - CHILLIEMAN HERE - ADD THIS FUNCTION!!!!!!!!
        db_insert_following(legend_id, legend_username, following_id, following_username)
        #except Exception as e:
        
        #    print("Seems this Following already exists!!")               

def get_next_token(request):
    try:
        return request['meta']['next_token']
    except KeyError as ke:
        return None

def consume_followers(legend_username, legend_twitter_id, json_response):
    try:
        users = json_response['data']
        process_followers(legend_twitter_id, legend_username, users)
    except KeyError as err:
        print("Thinking...")
        
    try:
        return json_response['meta']['result_count']
    except KeyError as err:
        return 0
        
def consume_following(legend_username, legend_twitter_id, json_response):
    try:
        users = json_response['data']
        process_following(legend_twitter_id, legend_username, users)
    except KeyError as err:
        print("Thinking...")
        
    try:
        return json_response['meta']['result_count']
    except KeyError as err:
        return 0
        
        

def entry_pull_followers(username, twitter_id, token):
    url = create_url_followers_by_id(twitter_id)
    
    json_response = connect_to_endpoint_followers_by_id(url, token)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    global running_total
    running_total += consume_followers(username, twitter_id, json_response)
    return get_next_token(json_response)
    
def entry_pull_followings(username, twitter_id, token):
    url = create_url_following_by_id(twitter_id)
    
    json_response = connect_to_endpoint_followers_by_id(url, token)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    global running_total
    running_total += consume_following(username, twitter_id, json_response)
    return get_next_token(json_response)
        

def main():        
    global running_total
    
    picker_header(["Hello Chillieman!"], '👋', True)
    time.sleep(1)
    
    picker_header(["Generating Unfollow List for:", legend_un], '😎', True)
    time.sleep(2)

    legend = connect_to_endpoint_fetch_user_by_username(legend_un)

    legend_data = legend['data'][0]
    legend_username = legend_data['username']
    legend_profile_name = legend_data['name']
    legend_twitter_id = legend_data['id']

    #Pull Followers for Featured Legend:
    next_token = entry_pull_followers(legend_username, legend_twitter_id,  None)
    while next_token != None:
        picker_header(["Checking Followers!"], '/', False)
        time.sleep(1)
        next_token = entry_pull_followers(legend_username, legend_twitter_id, next_token)
    else:
        picker_header(["Pulled All Followers for ->", " ", "@{}".format(legend_username)], '😊', True)
        time.sleep(1)
        
        
    #Pull People that Legend is Following!
    next_token = entry_pull_followings(legend_username, legend_twitter_id,  None)
    while next_token != None:
        picker_header(["Lets see who the Legend is following!!"], '/', False)
        time.sleep(1)
        next_token = entry_pull_followings(legend_username, legend_twitter_id, next_token)
    else:
        picker_header(["You BETTER be following ->", "@{}".format(legend_username)], '😊', True)
    
    
    #Pull All People The Legend Is Following:
    legend_is_following_list = db_fetch_all_people_legend_is_following(legend_username)

    final_list = []
    for following in legend_is_following_list:
        if not db_is_following_by_twitter_id(legend_id, following['id']):
            final_list.append(following['username'])
    
    picker_header(["UNFOLLOW THEM!!"], '😈', True)
    for final in final_list:
        print("@{}".format(final))

if __name__ == "__main__":
    main()
