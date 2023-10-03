import sqlite3
import time
from chillie_util import pooh_header, picker_header

DB_NAME = 'ChilliePicker.db'

# Data:
# blacklist
# - twitter_id
# - username
# - display_name
# - timestamp

ACTION_TYPE_LIKE="LIKE"
ACTION_TYPE_RETWEET="RETWEET"
ACTION_TYPE_QUOTE="QUOTE"
ACTION_TYPE_REPLY="REPLY"

AUDIT_TYPE_POOH="POOH"
AUDIT_TYPE_SCAMMER="SCAMMER"

def db_create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # This is a table to hold Twitter Users that fell for a honeypot - They are disqualified from Giveaways.
    c.execute("""CREATE TABLE pooh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL,
                profile_name TEXT NOT NULL,
                host_post_id TEXT NOT NULL,
                post_id TEXT NULL,
                content TEXT NULL
            )""")

    c.execute("""CREATE TABLE follower (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL,
                follower_id TEXT NOT NULL,
                follower_username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE following (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL,
                following_id TEXT NOT NULL,
                following_username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE entry_like (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE entry_retweet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")
    c.execute("""CREATE TABLE entry_quote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")
    c.execute("""CREATE TABLE extra_ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                username TEXT NOT NULL,
                amount INT NOT NULL
            )""")
    c.execute("""CREATE TABLE entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE disqualified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE winner (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL
            )""")

    c.execute("""CREATE TABLE trolled (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                message TEXT NOT NULL
            )""")
    
    c.execute("""CREATE TABLE scammer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL,
                scam_address TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_type TEXT NOT NULL,
                epoch_time REAL NOT NULL
            )""")
            
    c.execute("""CREATE TABLE audit_entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                audit_type TEXT NOT NULL,
                twitter_id TEXT NOT NULL,
                username TEXT NOT NULL,
                profile_name TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE golden (
                username TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE tweet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                author_id TEXT NOT NULL
            )""")
            
    c.execute("""CREATE TABLE airdrop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet TEXT NOT NULL
            )""")
            
    conn.commit()
    conn.close()


def db_fetch_all_pooh():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM pooh")
    
    all_pooh = c.fetchall()

    conn.close()
    return all_pooh
    
def db_fetch_all_tweets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT text FROM tweet")
    
    all_tweets = c.fetchall()
    
    tweet_text_list = []
    for t in all_tweets:
        tweet_text_list.append(t[0])

    conn.close()
    return tweet_text_list

# Temp Function - TODO - Remove me!
def db_fetch_all_unique_pooh():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT DISTINCT twitter_id, username, profile_name FROM pooh")
    
    all_pooh = c.fetchall()

    conn.close()
    
    pooh_data = []
    for pooh in all_pooh:
        piece_of_pooh = {'twitter_id': pooh[0], 'username': pooh[1], 'profile_name': pooh[2]}
        pooh_data.append(piece_of_pooh)
        
    return pooh_data
    
def db_fetch_all_unique_scammer():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT DISTINCT twitter_id, username, scam_address FROM scammer")
    
    all_pooh = c.fetchall()

    conn.close()
    
    pooh_data = []
    for pooh in all_pooh:
        piece_of_pooh = {'twitter_id': pooh[0], 'username': pooh[1], 'profile_name': pooh[2]}
        pooh_data.append(piece_of_pooh)
        
    return pooh_data
    
    
def db_fetch_all_unique_pooh_ids():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT DISTINCT twitter_id FROM pooh")
    
    all_pooh_ids = c.fetchall()

    conn.close()
    
    # Unwrap SQL Columns to extract TwitterIds
    unwrapped_ids = []
    for pooh in all_pooh_ids:
        unwrapped_ids.append(pooh[0])
        
    return unwrapped_ids
    
def db_fetch_all_unique_scammer_ids():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT DISTINCT twitter_id FROM scammer")
    
    all_pooh_ids = c.fetchall()
    
    conn.close()
    
    # Unwrap SQL Columns to extract TwitterIds
    unwrapped_ids = []
    for pooh in all_pooh_ids:
        unwrapped_ids.append(pooh[0])
        
    return unwrapped_ids

def db_picker_get_extra_ticket(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM extra_ticket WHERE post_id=:post_id", {'post_id': post_id})
    
    extra_ticket_list = c.fetchall()
    
    return_data = []
    
    for u in extra_ticket_list:
        try:
            username = u[2]
            entry = db_fetch_entry_by_username(post_id, username)
            
            data = {'twitter_id': None, 'amount': None}
            data['twitter_id'] = entry[1]
            data['amount'] = u[3]
            if db_is_pooh(data['twitter_id']):
                pooh_header(["Smells like Honey!!", "No Tickets for them!"], '🍯', True)
                db_disqualify_entry(post_id, data['twitter_id'])
            else:
                return_data.append(data)
                    
        except Exception as e:
            print("Extra Tickets Invalid Because They Are not in Entry List")
            
    conn.close()
    return return_data

def db_picker_likes_and_retweets_multiple(post_id, in_statement, count):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""SELECT entry_like.post_id, entry_like.twitter_id, entry_like.username
                FROM entry_like
                JOIN entry_retweet
                ON entry_like.post_id = entry_retweet.post_id
                AND entry_like.twitter_id = entry_retweet.twitter_id
                AND entry_like.username = entry_retweet.username
                WHERE entry_like.post_id IN ('1654948831094603776', '1654950165852172290')
                GROUP BY entry_like.twitter_id
                HAVING COUNT(*) >= :count
            """,{'in_statement': in_statement, 'count':count})
    
    all_potentials = c.fetchall()
    
    valid = []
    
    # DONE - Check if any exists in pooh
    for u in all_potentials:
        data = {'post_id': post_id, 'twitter_id': None, 'username': None}
        data['twitter_id'] = u[1]
        data['username'] = u[2]
        if db_is_pooh(data['twitter_id']):
            db_insert_disqualified(post_id, data['twitter_id'], data['username'])
        else:
            valid.append(data)
            db_insert_entry(post_id, data['twitter_id'], data['username'])

    conn.close()
    return valid

def db_picker_likes_and_retweets(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # TODO: Update this to Join the entry_like and entry_retweet tables.
    c.execute("""SELECT entry_like.post_id, entry_like.twitter_id, entry_like.username
                FROM entry_like
                JOIN entry_retweet
                ON entry_like.post_id = entry_retweet.post_id
                AND entry_like.twitter_id = entry_retweet.twitter_id
                AND entry_like.username = entry_retweet.username
                WHERE entry_like.post_id = :post_id
            """,{'post_id': post_id})
    
    all_potentials = c.fetchall()
    
    valid = []
    
    # DONE - Check if any exists in pooh
    for u in all_potentials:
        data = {'post_id': post_id, 'twitter_id': None, 'username': None}
        data['twitter_id'] = u[1]
        data['username'] = u[2]
        if db_is_pooh(data['twitter_id']):
            db_insert_disqualified(post_id, data['twitter_id'], data['username'])
        else:
            valid.append(data)
            db_insert_entry(post_id, data['twitter_id'], data['username'])

    conn.close()
    return valid
    
def db_picker_likes(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Select everyone who liked the giveaway
    c.execute("""SELECT post_id, twitter_id, username
                FROM entry_like
                WHERE post_id = :post_id
            """,{'post_id': post_id})
    
    all_potentials = c.fetchall()
    
    valid = []
    
    # DONE - Check if any exists in pooh
    for u in all_potentials:
        data = {'post_id': post_id, 'twitter_id': None, 'username': None}
        data['twitter_id'] = u[1]
        data['username'] = u[2]
        if db_is_pooh(data['twitter_id']):
            db_insert_disqualified(post_id, data['twitter_id'], data['username'])
        else:
            valid.append(data)
            db_insert_entry(post_id, data['twitter_id'], data['username'])

    conn.close()
    return valid
    
def db_picker_retweets(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Select everyone who retweeted the giveaway
    c.execute("""SELECT post_id, twitter_id, username
                FROM entry_retweet
                WHERE post_id = :post_id
            """,{'post_id': post_id})
    
    all_potentials = c.fetchall()
    
    valid = []
    
    # DONE - Check if any exists in pooh
    for u in all_potentials:
        data = {'post_id': post_id, 'twitter_id': None, 'username': None}
        data['twitter_id'] = u[1]
        data['username'] = u[2]
        if db_is_pooh(data['twitter_id']):
            db_insert_disqualified(post_id, data['twitter_id'], data['username'])
        else:
            valid.append(data)
            db_insert_entry(post_id, data['twitter_id'], data['username'])

    conn.close()
    return valid
    
def db_disqualify_entry(post_id, twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM entry WHERE post_id=:post_id AND twitter_id=:twitter_id", {'post_id': post_id, 'twitter_id': twitter_id})
    
    loser = c.fetchone()
    try:
        data = {'post_id': post_id, 'twitter_id': twitter_id, 'username': None}
        data['username'] = loser[3]
        
        db_insert_disqualified(post_id, data['twitter_id'], data['username'])
    except Exception as e:
        print("A Noob wasnt following the Legend!".format(twitter_id))

    conn.close()
    return loser
    
def db_pull_winner(post_id, twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM entry WHERE post_id=:post_id AND twitter_id=:twitter_id", {'post_id': post_id, 'twitter_id': twitter_id})
    
    winner = c.fetchone()
    
    data = {'post_id': post_id, 'twitter_id': None, 'username': None}
    data['twitter_id'] = winner[2]
    data['username'] = winner[3]
    
    db_insert_winner(post_id, data['twitter_id'], data['username'])

    conn.close()
    return data

def db_fetch_entry(post_id, twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM entry WHERE post_id=:post_id AND twitter_id=:twitter_id", {'post_id': post_id, 'twitter_id': twitter_id})
    
    all_entries = c.fetchall()

    conn.close()
    return all_pooh
    
def db_fetch_entry_by_username(post_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM entry WHERE post_id=:post_id AND username=:username", {'post_id': post_id, 'username': username})
    
    entry = c.fetchone()

    conn.close()
    return entry
    
    
def db_fetch_all_entries_by_post_id(post_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM entry WHERE post_id=:post_id", {'post_id': post_id})
    
    all_entries = c.fetchall()

    conn.close()
    return all_entries
    
    
def db_fetch_all_people_legend_is_following(legend_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT following_id, following_username FROM following WHERE twitter_id=:legend_id", {'legend_id': legend_id})
    
    all_entries = c.fetchall()
    
    data_return = []
    for d in all_entries:
        omfg = {'id': d[0], 'username': d[1]}
        data_return.append(omfg)

    conn.close()
    return data_return
    
def db_insert_wallet(wallet):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO airdrop VALUES (null, :wallet)", 
            {'wallet': wallet}
        )

    conn.commit()
    conn.close()
    
def db_insert_tweet(text, author_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO tweet VALUES (null, :text, :author_id)", 
            {'text': text, 'author_id': author_id}
        )

    conn.commit()
    conn.close()

def db_insert_follower(twitter_id, username, follower_id, follower_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO follower VALUES (null, :twitter_id, :username, :follower_id, :follower_username)", 
            {'twitter_id': twitter_id, 'username': username, 'follower_id': follower_id, 'follower_username': follower_username}
        )

    conn.commit()
    conn.close()
    
def db_insert_following(twitter_id, username, following_id, following_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO following VALUES (null, :twitter_id, :username, :following_id, :following_username)", 
            {'twitter_id': twitter_id, 'username': username, 'following_id': following_id, 'following_username': following_username}
        )

    conn.commit()
    conn.close()
    

def db_insert_entry_like(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO entry_like VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()

def db_insert_entry_retweet(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO entry_retweet VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()
    
def db_insert_entry_quote(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("INSERT INTO entry_quote VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()
    

# Inserts:
def db_insert_extra_ticket(host_post_id, username, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO extra_ticket VALUES (null, :host_post_id, :username, :amount)", 
            {'host_post_id': host_post_id, 'username': username, 'amount': amount}
        )

    conn.commit()
    conn.close()
    
    
def db_insert_entry(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print("Valid Entry! -> {}".format(username))
    c.execute("INSERT INTO entry VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()
    
def db_insert_disqualified(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print("Disqualified! -> {}".format(username))
    c.execute("INSERT INTO disqualified VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()
    
def db_insert_winner(host_post_id, twitter_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO winner VALUES (null, :host_post_id, :twitter_id, :username)", 
            {'host_post_id': host_post_id, 'twitter_id': twitter_id, 'username': username}
        )

    conn.commit()
    conn.close()

def db_insert_scammer(twitter_id, username, scam_address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scammer VALUES (null, :twitter_id, :username, :scam_address)", 
            {'twitter_id': twitter_id, 'username': username, 'scam_address': scam_address}
        )

    conn.commit()
    conn.close()

def db_insert_pooh_like(twitter_id, username, profile_name, host_post_id):
    db_insert_pooh(ACTION_TYPE_LIKE, twitter_id, username, profile_name, host_post_id, "null", "null")
    
def db_insert_pooh_retweet(twitter_id, username, profile_name, host_post_id):
    db_insert_pooh(ACTION_TYPE_RETWEET, twitter_id, username, profile_name, host_post_id, "null", "null")
    
def db_insert_pooh_quote(twitter_id, username, profile_name, host_post_id, post_id, content):
    db_insert_pooh(ACTION_TYPE_QUOTE, twitter_id, username, profile_name, host_post_id, post_id, content)
    
def db_insert_pooh_reply(twitter_id, username, profile_name, host_post_id, post_id, content):
    db_insert_pooh(ACTION_TYPE_REPLY, twitter_id, username, profile_name, host_post_id, post_id, content)

def db_insert_pooh(action_type, twitter_id, username, profile_name, host_post_id, post_id, content):
    if db_is_golden(username):
        print("{} is Golden, they cannot be entered as Pooh!".format(username))
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("Eating {} Honey - {}".format(action_type, twitter_id))
    c.execute("INSERT INTO pooh VALUES (null, :action_type, :twitter_id, :username, :profile_name, :host_post_id, :post_id, :content)", 
            {'action_type': action_type,'twitter_id': twitter_id, 'username': username, 'profile_name': profile_name, 'host_post_id': host_post_id, 'post_id': post_id, 'content': content}
        )

    conn.commit()
    conn.close()

def db_insert_audit_returns_id(audit_type, epoch_time):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    new_audit_id = c.execute("INSERT INTO audit VALUES (null, :audit_type, :epoch_time)", 
            {'audit_type': audit_type, 'epoch_time': epoch_time}
        )

    print("Starting {} Audit - ID: {}".format(audit_type, new_audit_id))
    conn.commit()
    conn.close()
    return new_audit_id
    

def db_insert_audit_pooh(audit_id, twitter_id, username, profile_name):
    db_insert_audit_entry(audit_id, AUDIT_TYPE_POOH, twitter_id, username, profile_name)
    
def db_insert_audit_scammer(audit_id, twitter_id, username, profile_name):
    db_insert_audit_entry(audit_id, AUDIT_TYPE_SCAMMER, twitter_id, username, profile_name)
    
def db_insert_audit_entry(audit_id, audit_type, twitter_id, username, profile_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print("Inserting {} Audit[{}] Entry -> {}".format(audit_type, audit_id, twitter_id))
    c.execute("INSERT INTO audit_entry VALUES (null, :audit_id, :audit_type, :twitter_id, :username, :profile_name)", 
            {'audit_id': audit_id, 'audit_type': audit_type,'twitter_id': twitter_id, 'username': username, 'profile_name': profile_name}
        )

    conn.commit()
    conn.close()

def db_is_golden(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM golden WHERE username=:username",
            {'username': username}
        )
    
    golden_count = c.fetchone()
    conn.close()     
        
    if golden_count[0] > 0:
        return True
    return False
    
# Does question_twitter_id follow this username?
def db_is_following_by_username(username, question_twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM follower WHERE username=:username AND follower_id=:question_twitter_id",
            {'username': username, 'question_twitter_id': question_twitter_id}
        )
    
    pooh_count = c.fetchone()
    conn.close()     
        
    if pooh_count[0] > 0:
        print("Contestant is following @{}".format(username))
        return True
    print("Contestant is NOT following @{}".format(username))
    return False

# Does question_twitter_id follow the featured twitter_id?
def db_is_following_by_twitter_id(twitter_id, question_twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM follower WHERE twitter_id=:twitter_id AND follower_id=:question_twitter_id",
            {'twitter_id': twitter_id, 'question_twitter_id': question_twitter_id}
        )
    
    pooh_count = c.fetchone()
    conn.close()     
        
    if pooh_count[0] > 0:
        return True
    return False
    

def db_is_pooh(twitter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM pooh WHERE twitter_id=:twitter_id",
            {'twitter_id': twitter_id}
        )
    
    pooh_count = c.fetchone()
    conn.close()     
        
    if pooh_count[0] > 0:
        return True
    return False
    
def db_is_pooh_existing(action_type, twitter_id, host_post_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM pooh WHERE action_type=:action_type AND twitter_id=:twitter_id AND host_post_id=:host_post_id AND username=:username ",
            {'action_type': action_type,'twitter_id': twitter_id, 'username': username, 'host_post_id': host_post_id}
        )
    
    pooh_count = c.fetchone()
    conn.close()     
        
    if pooh_count[0] > 0:
        return True
    return False
    
    
def db_clear_follower_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM follower")

    conn.commit()
    conn.close()
    
def db_clear_entry_potentials(post_id):
    #Repick This Giveaway
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM entry_like WHERE post_id=:post_id", {'post_id': post_id})
    c.execute("DELETE FROM entry_retweet WHERE post_id=:post_id", {'post_id': post_id})
    c.execute("DELETE FROM entry_quote WHERE post_id=:post_id", {'post_id': post_id})

    conn.commit()
    conn.close()
    
def db_clear_previous_picks(post_id):
    #Repick This Giveaway
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM entry WHERE post_id=:post_id", {'post_id': post_id})
    c.execute("DELETE FROM disqualified WHERE post_id=:post_id", {'post_id': post_id})
    c.execute("DELETE FROM winner WHERE post_id=:post_id", {'post_id': post_id})

    conn.commit()
    conn.close()