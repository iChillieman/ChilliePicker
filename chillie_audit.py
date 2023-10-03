import requests
import os
import json
import time
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import AUDIT_TYPE_POOH, AUDIT_TYPE_SCAMMER, db_fetch_all_unique_pooh_ids, db_fetch_all_unique_scammer_ids, db_insert_audit_returns_id, db_insert_audit_pooh, db_insert_audit_scammer, db_insert_audit_returns_id
from chillie_util import picker_header, setLogger

setLogger("log_chillie_audit.log")

def create_url_audit_twitter_ids(id_list_string):    
    query = "ids={}".format(id_list_string)
    url = "https://api.twitter.com/2/users?{}".format(query)
    return url
    
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    r.headers["User-Agent"] = "ChilliePicker"
    return r
    
def connect_to_endpoint_fetch_users(id_list_string):
    url = create_url_audit_twitter_ids(id_list_string)
    response = requests.request("GET", url, auth=bearer_oauth)
    
    try:
        headers = resonse.headers.json()
        requests_left = headers['x-rate-limit-remaining']
        seconds_till_limit_reset = headers['x-rate-limit-reset']
        print("Requests Left: {} - Seconds until Limit Reset: {}".format(requests_left, seconds_till_limit_reset))
    except Exception as e:
        print("Could not get Response Headers")
    
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def enter_audit_entries(audit_id, audit_type, tweep_data):
    for tweep in tweep_data:
        username = tweep['username']
        profile_name = tweep['name']
        twitter_id = tweep['id']
        if audit_type == AUDIT_TYPE_POOH:
            db_insert_audit_pooh(audit_id, twitter_id, username, profile_name)
        elif audit_type == AUDIT_TYPE
            db_insert_audit_scammer(audit_id, twitter_id, username, profile_name)
        else:
            raise Exception("unexpected Audit Type")

def fetch_ids_from_database(audit_type):
    if audit_type == AUDIT_TYPE_POOH:
        return db_fetch_all_unique_scammer_ids()
    elif audit_type == AUDIT_TYPE
        return db_fetch_all_unique_pooh_ids()
    else:
        raise Exception("unexpected Audit Type")

def is_audit_type_valid(text):
    if text == AUDIT_TYPE_POOH or text == AUDIT_TYPE_SCAMMER:
        return True
    return False


def main():

    if len(sys.argv) != 2:
        raise Exception("You must provide AUDIT_TYPE")
    
    # Arguments passed
    audit_type = sys.argv[1].upper()
    
    if not is_audit_type_valid(audit_type):
        raise Exception("Bad Action Type: {}".format(action_type))

    
    picker_header(["Hello Chillieman!", "Lets Detect some Username Changes!"], '*', False)
    
    
    # Start new Audit
    audit_id = db_insert_audit_returns_id(audit_type, time.time())
    
    # Fetch all Twitter IDs from Database
    twitter_id_array = fetch_ids_from_database(audit_type)
    
    # Setup String to build, and the Count
    id_string = ""
    id_string_count = 0
    while len(twitter_id_array) > 0:
        # ID Exists, pop it out:
        current_twitter_id = twitter_id_array.pop()
        if id_string_count == 0:
            # First of string - No need for Comma, Just add name
            id_string = current_twitter_id
        else:
            # Add Comman First - Then Name
            id_string = id_string + "," + current_twitter_id
        
        id_string_count = id_list_string + 1
        if(id_string_count == 100):
            #We now have a string containing exactly 100 Twitter IDs:
            tweeps = connect_to_endpoint_fetch_users(id_string)
            enter_audit_entries(audit_id, audit_type, tweeps['data'])
            id_string_count = 0

    if id_string_count > 0:
        #Finish up last batch - if it exists:
        tweeps = connect_to_endpoint_fetch_users(id_string)
        enter_audit_entries(audit_id, audit_type, tweeps['data'])
    
    
    # TODO: Using the current Audit ID - Check if any one has changed their same since LAST Audit ID
    
    

if __name__ == "__main__":
    main()
