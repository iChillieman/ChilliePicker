from chillie_picker_db import db_create_tables, db_fetch_all_tweets, db_insert_wallet
from chillie_util import setLogger, picker_header

setLogger("log_airdrop_2.log")

for tweet in db_fetch_all_tweets():
    index = tweet.find("0x")
    if index != -1:
        ending_index = index + 42
        stop_at = len(tweet) 
        address = tweet[index:ending_index]
        print(address)
        db_insert_wallet(address)