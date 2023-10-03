import requests
import os
import json
import time
import sys
import random
import emoji
from chillie_util import setLogger, pooh_header, picker_header
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import ACTION_TYPE_LIKE, ACTION_TYPE_RETWEET, ACTION_TYPE_QUOTE, ACTION_TYPE_REPLY, db_insert_entry_like, db_insert_entry_retweet, db_picker_likes_and_retweets, db_picker_retweets, db_picker_likes, db_insert_follower, db_picker_get_extra_ticket, db_is_following_by_twitter_id, db_pull_winner, db_insert_disqualified, db_disqualify_entry, db_clear_follower_table, db_clear_entry_potentials, db_clear_previous_picks, db_picker_likes_and_retweets_multiple

setLogger("log_fren_chillie_picker.log")

running_total = 0

# Search Flags:
SEARCH_FOR_LIKES = "L"
SEARCH_FOR_RETWEETS = "R"
SEARCH_FOR_BOTH = "B"

# What are Qualifications for Giveaway?
search_for = "B"

# Who must Users follow? (Supports Multiple Accounts)
must_follow = []

# Which Giveaway Post is this?
post_id = "1654948831094603776"

required_post_entries = ["1654948831094603776", "1654950165852172290"]

# True if you want to stop the script after Collecting Entry (Likes / Retweets)
just_collect_potential_entries = False

# How many Winners?
winner_count = 1

# Make this FALSE if you have already pulled Followers:
must_pull_followers = False

# Clear Existing Likes / Retweets pulled from Giveaway Posts? 
# False if you want to Repick - But dont want to fetch more data from Twitter.
must_pull_entry_qualifications = False

# Clear Existing Entries and Disqualified Entries??
must_clear_previous_pick = True

def create_url_pull_featured_account(username):    
    username_string = "usernames={}".format(username)
    url = "https://api.twitter.com/2/users/by?{}".format(username_string)
    return url
    
def create_url_followers_by_id(twitter_id):
    return "https://api.twitter.com/2/users/{}/followers".format(twitter_id)
    
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
    
def connect_to_endpoint(url, next_token):
    if next_token == None:
        queries = {'max_results': 100}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    else:
        queries = {'pagination_token': next_token, 'max_results': 100}
        response = requests.request("GET", url, auth=bearer_oauth, params=queries)
    
    if response.status_code == 429:
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
        try:
            if action_type == ACTION_TYPE_LIKE:
                db_insert_entry_like(host_post_id, twitter_id, username)
            if action_type == ACTION_TYPE_RETWEET:
                db_insert_entry_retweet(host_post_id, twitter_id, username)
        except Exception as e:
            print("Seems this already exists!!")

def process_followers(legend_id, legend_username, users):
    for u in users:
        follower_id = u['id']
        follower_id = u['username']
        try:
            db_insert_follower(legend_id, legend_username, follower_id, follower_username)
        except Exception as e:
            print("Seems this already exists!!")             

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
        
def consume_likes_and_tweets(action_type, host_tweet_id, json_response):
    try:
        users = json_response['data']
        picker_header(["Loading {} Data".format(action_type)], '/', False)
        process_likes_and_retweets(action_type, host_tweet_id, users)
    except KeyError as err:
        picker_header(["Yummy {}s!".format(action_type)], '*', False)
        
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
        
def entry_likes_and_retweets(action_type, token, host_tweet_id):
    url = create_url_likes_and_retweets(action_type, host_tweet_id)
    
    json_response = connect_to_endpoint(url, token)
    #print(json.dumps(json_response, indent=4, sort_keys=True))
    global running_total
    running_total += consume_likes_and_tweets(action_type, host_tweet_id, json_response)
    return get_next_token(json_response)
    
def validate_search_for(search_flag):
    if search_for != SEARCH_FOR_LIKES and search_for != SEARCH_FOR_RETWEETS and search_for != SEARCH_FOR_BOTH:
        raise Exception("Invalid Search Flag - {}".format(search_for))

def main():        
    global running_total
    
    validate_search_for(search_for)
    # TODO - Validate Post ID
        
        
    if must_clear_previous_pick:
        #Clear Any Data from previous Runs of this script (Used for Repicks)
        db_clear_previous_picks(post_id)
    
    picker_header(["Hello Rocket!!"], '🚀', True)
    time.sleep(3)
    
    
    picker_header(["Lets Pick a Winner for Tweet ID:", post_id], '🚀', True)
    time.sleep(1)
    
    # First Sniff Likes if applicable:
    if must_pull_entry_qualifications:
        # Clear all previous Data For Likes / Retweets
        db_clear_entry_potentials(post_id)
        
        if search_for == SEARCH_FOR_BOTH or search_for == SEARCH_FOR_LIKES:
            picker_header(["Checking Likes"], '*', False)
            next_token = entry_likes_and_retweets(ACTION_TYPE_LIKE, None, post_id)
            while next_token != None:
                next_token = entry_likes_and_retweets(ACTION_TYPE_LIKE, next_token, post_id)
            else:
                message = ["I'm satisfied -", "There are {} Like Entries!!".format(running_total)]
                picker_header(message, '*', False)
        
        running_total = 0
        
        # Then Sniff Retweets:
        if search_for == SEARCH_FOR_BOTH or search_for == SEARCH_FOR_RETWEETS:
            picker_header(["Checking Retweets"], '*', False)
            
            next_token = entry_likes_and_retweets(ACTION_TYPE_RETWEET, None, post_id)
            while next_token != None:
                next_token = entry_likes_and_retweets(ACTION_TYPE_RETWEET, next_token, post_id)
            else:
                message = ["I'm satisfied -", "There are {} Retweet Entries!!".format(running_total)]
                picker_header(message, '*', False)
    else:
        picker_header(["Data is already Pulled!", "Just need to Pick Winner!"], '🚀', True)
        time.sleep(1)
        
    if just_collect_potential_entries:
        picker_header(["Just Pulling entries - Pick Winner Seperately."], '*', False)
        return
    
    picker_header(["Generating Potential Winners!"], '🚀', True)
    
    
    query = "('1654948831094603776', '1654950165852172290')"
    potential_winners = db_picker_likes_and_retweets_multiple('1654948831094603776', query, 2)
    
    # Construct a List with all potential users!
    pot = []
    for p in potential_winners:
        # Grab Each ID and put it into the pot
        pot.append(p['twitter_id'])
    
    
    winner_ids = []
    while len(winner_ids) < winner_count:
        #TODO: Remove this Try
        try:
            # Select from the List at Random
            index = random.randint(0,len(pot)) - 1
            potential_winner_id = pot[index]
            
            # No required Followers.
            winner_ids.append(potential_winner_id)
        except Exception as e:
            print("Something Went Wrong - Try again!")
                
    # Winner!!
    
    winners_for_message = []
    # Pull Winner from Entry DB:
    for winner_id in winner_ids:
        winner = db_pull_winner(post_id, winner_id)
        winners_for_message.append("@{}".format(winner['username']))
        
    if len(winner_ids) > 1:
        winners_for_message.insert(0, "Winners!!")
    else:
        winners_for_message.insert(0, "Winner!!")
    picker_header(winners_for_message, '🚀', True)
    

if __name__ == "__main__":
    main()
