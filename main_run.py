import argparse
import json
import requests
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tweepy
from tweepy import StreamListener
import ast
import time
import gzip

# Errors
from requests.exceptions import ConnectionError
  

class MyStreamListener(StreamListener):
    
    def __init__(self, output_path, no_per_file, compression = "gzip"):
        StreamListener.__init__(self)
        
        # Initialise counter and storage variables
        self._counter = 1
        self._output_path = output_path
        self._no_per_file = no_per_file
        self._data = []

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False    
        
    def on_status(self, status):
        """ Main method to output data into files from the Twitter stream. Number of statuses are defined by
        no_per_file attribute."""

        self._data.append(status._json)
        if self._counter % self._no_per_file == 0:
            # Get current date and output JSON
            date = time.strftime('%Y-%m-%d_%H-%M-%S', time.gmtime(time.time()))
            
            
            if compression == "None":
                # Save raw file
                file_name = "{}/{}.json".format(self._output_path,date)
                with open(file_name, 'w') as outfile:
                    json.dump(self._data, outfile)
        
            if compression == "gzip":
                file_name = "{}/{}.json.gz".format(self._output_path,date)
                
                json_str = json.dumps(self._data)              # 2. string (i.e. JSON)
                json_bytes = json_str.encode('utf-8')    # 3. bytes (i.e. UTF-8)
                
                with open(file_name, "w") as outfile:
                    outfile.write(json_bytes)
        
            # Add to counter and reset data storage
            self._counter += 1
            self._data = []
        else:
            self._counter += 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process proxy analysis inputs')

    parser.add_argument("output", help = "Output path for twitter data.")
    parser.add_argument("credentials", help = "Path to twitter development credentials. Expects JSON file.")
    parser.add_argument("--no_tweets", dest = "no_tweets", help = "Save every N number of tweets.", default=1000, type=int )
    parser.add_argument("--bbox", dest = "bbox", help = "Bounding box for the tweets selection.", default = (-13.4139, 49.1621, 1.7690, 60.8547))
    parser.add_argument("--timeout", dest = "timeout", help = "Timeout in case of an error.", default = 60)
    parser.add_argument("--compression", dest = "compression", help = "Compression type.", default = "gzip")
        
    credentials_path = parser.parse_args().credentials
    output_path = parser.parse_args().output
    no_tweets = parser.parse_args().no_tweets
    locations = parser.parse_args().bbox
    timeout = parser.parse_args().timeout
    compression = parser.parse_args().compression
        
    with open(credentials_path,"r") as fp:
        credentials = json.load(fp)
    
    while True:
        try:
            auth = tweepy.OAuthHandler(credentials["CONSUMER_KEY"], credentials["CONSUMER_SECRET"])
            auth.set_access_token(credentials["ACCESS_TOKEN"], credentials["ACCESS_SECRET"])
            api = tweepy.API(auth,wait_on_rate_limit=True)

            myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener(output_path, no_tweets, compression = compression))

            myStream.filter(locations=locations)
        except ConnectionError:
            print("Error encountered sleeping for 60 seconds.")
            time.sleep(timeout)
            
    ### Useful locations
    
    # syria = (35.7270, 32.3106, 42.3850, 37.3190)
    # uk = (-13.4139, 49.1621, 1.7690, 60.8547)
    

    
