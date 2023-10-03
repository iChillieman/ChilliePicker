import requests
import os
import json
import time
import random
import emoji
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import db_insert_scammer
from chillie_util import pooh_header, picker_header, setLogger

setLogger("log_scammers.log")

scammer_usernames = "babywolfe25,Blessed_nife16"
wallet_address = '0xbe84959b5bfF8d2C3BFEEff94000eBB0C7Ee2BD5'

def create_url_pull_featured_account(username):    
    username_string = "usernames={}".format(username)
    url = "https://api.twitter.com/2/users/by?{}".format(username_string)
    return url
    
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    r.headers["User-Agent"] = "ChilliePicker"
    return r
    
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

scammers = connect_to_endpoint_fetch_user_by_username(scammer_usernames)
scammers_data = scammers['data']
messages = []
for s in scammers_data:
    scammer_username = s['username']
    scammer_profile_name = s['name']
    scammer_twitter_id = s['id']
    messages.append("@{}".format(scammer_username))
    
    db_insert_scammer(scammer_twitter_id, scammer_username, wallet_address)


if len(messages) > 1:
    message = "Ew Scammers!"
else:
    message = "Ew Scammer!"
    
messages.insert(0, message)
messages.insert(0, " ")
messages.insert(0, wallet_address)

messages.append(" ")
messages.append("Ill keep an eye on em,")
messages.append("Thank you!!")
messages.append(" ")


picker_header(messages, '!', False)


