import requests
import os
import json
import time
import random
import emoji
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import db_insert_scammer
from chillie_util import pooh_header, picker_header, setLogger

setLogger("log_fetch_users_by_id.log")

ids = "1654510408005287936,1617530226409639937"

def create_url_pull_featured_account(scammer_ids):
    query = "ids={}".format(scammer_ids)
    url = "https://api.twitter.com/2/users?{}".format(query)
    return url
    
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    r.headers["User-Agent"] = "ChilliePicker"
    return r
    
def connect_to_endpoint_fetch_user_by_ids(scammer_ids):
    url = create_url_pull_featured_account(scammer_ids)
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

users = connect_to_endpoint_fetch_user_by_ids(ids)
print(users)
data = users['data']
messages = []
for u in data:
    username = u['username']
    profile_name = u['name']
    twitter_id = u['id']
    messages.append("@{}".format(username))
    messages.append("Name: {}".format(profile_name))
    messages.append("ID: {}".format(twitter_id))


picker_header(messages, '*', False)


