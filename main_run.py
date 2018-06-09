import argparse
import json
import requests
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tweepy
from tweepy import StreamListener
import ast
  

class MyStreamListener(StreamListener):
    
    def __init__(self, output_path):
        StreamListener.__init__(self)
        
        # Initialise counter and storage variables
        self._counter = 1
        self._output_path = output_path
        self._data = []

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False    
        
    def on_status(self, status, no_per_file = 1000):
        """ Main method to output data into files from the Twitter stream. Number of statuses are defined by
        no_per_file attribute."""

        self._data.append(status._json)
        if self._counter % no_per_file == 0:
            file_name = "{}/{}.json".format(self._output_path,self._counter)
            with open(file_name, 'w') as outfile:
                json.dump(self._data, outfile)
        
            # Add to counter and reset data storage
            self._counter += 1
            self._data = []
        else:
            self._counter += 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process proxy analysis inputs')

    parser.add_argument("output", help = "Output path for twitter data.")
    parser.add_argument("credentials", help = "Path to twitter development credentials. Expects JSON file.")
    
    print(parser.parse_args().credentials)
    
    credentials_path = parser.parse_args().credentials
    output_path = parser.parse_args().output
    
    with open(credentials_path,"r") as fp:
        credentials = json.load(fp)
    
    auth = tweepy.OAuthHandler(credentials["CONSUMER_KEY"], credentials["CONSUMER_SECRET"])
    auth.set_access_token(credentials["ACCESS_TOKEN"], credentials["ACCESS_SECRET"])
    api = tweepy.API(auth,wait_on_rate_limit=True)

    myStreamListener = MyStreamListener(output_path)
    myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener(output_path))

    syria = (35.7270, 32.3106, 42.3850, 37.3190)
    myStream.filter(locations=syria)
    
