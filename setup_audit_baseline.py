import requests
import os
import json
import time
import random
import emoji
from config import TWITTER_BEARER_TOKEN
from chillie_picker_db import db_fetch_all_unique_pooh, db_fetch_all_unique_scammer, db_insert_audit_pooh, db_insert_audit_scammer
from chillie_util import pooh_header, picker_header, setLogger

picker_header(["Hello Chillieman!", "Creating Baseline In Database"], "*", False)
time.sleep(1)

for p in db_fetch_all_unique_pooh():
    db_insert_audit_pooh(1, p['twitter_id'], p['username'], p['profile_name'])
    
for p in db_fetch_all_unique_scammer():
    db_insert_audit_scammer(2, p['twitter_id'], p['username'], p['profile_name'])
    
picker_header(["Database is setup,", "You can now detect Username changes!!"], "🥳", True)