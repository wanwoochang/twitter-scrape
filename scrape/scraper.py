import os, re, json, time

import datetime as dt
from dateutil import relativedelta

import tweepy

#Query to scrape Twitter
query = ["new year resolution", "2020 is the year", "#resolutions2020"]

#Define folders
folder_main = os.getcwd()
folder_creds = r"D:\personal\creds\twitter"
folder_dump = os.path.join(folder_main, "dump")

foldername = "_".join([q.replace(" ", "") for q in query])
folder_dump_query = os.path.join(folder_dump, foldername)

if foldername not in os.listdir(folder_dump):
    os.mkdir(folder_dump_query)

for file in os.listdir(folder_creds):
    filepath = os.path.join(folder_creds, file)
    with open(filepath, "r") as f:
        globals()[file.split(".")[0]] = json.load(f)

        
#Define Twitter streamer
class StreamListener(tweepy.StreamListener):
    
    def on_status(self, status):
        print(status.text)
    
    def on_error(self, status_code):
        if status_code == 420:
            return False
        
    def on_data(self, data):
        raw_tweet = json.loads(data)
        
        try:
            with open(os.path.join(folder_dump_query, f"{raw_tweet['id']}.json"), "w") as f:
                json.dump(raw_tweet, f)
        except:
            pass
        
    def start_stream(stream, **kwargs):
        try:
            stream.filter(**kwargs)
        except ReadTimeoutError:
            stream.disconnect()
            logger.exception("ReadTimeoutError exception")
            start_stream(stream, **kwargs)
        
#Sign in to Twitter
auth = tweepy.OAuthHandler(consumer_key=consumer["key"], consumer_secret=consumer["secret"])
auth.set_access_token(key=token["key"], secret=token["secret"])

api = tweepy.API(auth)

#Set up streamer
listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, 
                       listener=listener)

stream.filter(track=query, 
              languages=["en"], 
              is_async=True)