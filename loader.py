#!/usr/bin/env python3

#
# FETCH_STATS.PY: fetches stats and stores stats for later usage
#
# The filename the bearer token is read from is defined by BEARER_FILE_NAME 
#

import tweepy
import datetime
import csv

CONSUMER_KEY_FILE = "CONSUMER_KEY"
ACCESS_KEY_FILE = "ACCESS_KEY"
WSRC_TWITTER_ID = ""

def init_api():
    try:
        consumer_key, consumer_secret = "", ""
        access_token, access_secret = "", ""
        with open(CONSUMER_KEY_FILE, "r") as f:
            consumer_key = f.readline().strip()
            consumer_secret = f.readline().strip()
        with open(ACCESS_KEY_FILE, "r") as f:
            access_token = f.readline().strip()
            access_secret = f.readline().strip()
        return tweepy.Client (
                   consumer_key=consumer_key, consumer_secret=consumer_secret,
                   access_token=access_token, access_token_secret=access_secret
               )
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error accessing the bearer token file: {e}")
    except Exception as e:
        print(f"Error initializing Twitter API: {e}")
    return None

def get_day_stats(cli, date):
    tweets = client.get_users_tweets(screen_name="WesternWeightRm", since_id="1713549757023436953")

client = init_api()

# Oct 14, 2023
tweets = 
poop = []
for t in tweets:
    poop.append({"time": t.created_at, "text": t.text})

print(poop)
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["time", "text"])
    writer.writeheader()
    for e in poop:
        writer.writerow(e)
