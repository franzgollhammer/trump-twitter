from tweepy import OAuthHandler # For OAuth authentication
from tweepy import API
from tweepy import Cursor

import numpy as np
import pandas as pd
import time

# Import file with twitter credentials from https://developer.twitter.com/
import twitter_credentials


# Function to convert JSON object into pandas dataframe
# (Table with colums and rows)
def tweets_to_df(tweets):
    df = pd.DataFrame(
        data=[tweet.full_text for tweet in tweets], columns=["tweets"])
    df["id"] = np.array([tweet.id for tweet in tweets])
    df["length"] = np.array([len(tweet.full_text) for tweet in tweets])
    df["date"] = np.array([tweet.created_at for tweet in tweets])
    df["source"] = np.array([tweet.source for tweet in tweets])
    df["likes"] = np.array([tweet.favorite_count for tweet in tweets])
    df["retweets"] = np.array([tweet.retweet_count for tweet in tweets])

    return df

# Class to authenticate for twitter API
class Authenticator:
    """ Authenticator for twitter api
        - authenticate function returns auth object for authentication
    """

    def authenticate(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY,
                            twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN,
                              twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterCli:
    """ Twitter client class:
        - arg twitter_user targets the user to get data from.
    """

    # On initialization authenticate via Authenticator class
    # and create API connection
    def __init__(self, twitter_user=None):
        self.auth = Authenticator().authenticate()
        self.twitter_cli = API(self.auth)
        self.twitter_user = twitter_user

    # Helper function to return client
    def get_cli_api(self):
        return self.twitter_cli

    # Function to fetch a list of tweets from specified user
    def get_timeline_tweets(self, num_tweets=100, max_id=None):
        self.max_id = max_id
        self.num_tweets = num_tweets
        self.api = self.twitter_cli

        data = self.Cursor(api.user_timeline(
            screen_name=self.twitter_user,
            count=self.num_tweets,
            tweet_mode="extended",
            max_id=self.max)).items(200)

        # return a list of tweets
        return data

    # Function to return a collection of tweet lists
    # because API only returns 200 tweets per request
    # There is a total limitation of Tweets u can fetch (ca. 3200)
    def get_tweet_collection(self, total_num_tweets=1000):
        self.total_num_tweets = total_num_tweets
        tweets_list = []

        # Initialization feed for tweet list
        data = self.get_timeline_tweets(max_id=None)

        for tweet in data:
            tweets_list.append(tweet)

        # convert tweets list to dataframe
        df = tweets_to_df(data)

        # Initial write to csv file
        df.to_csv("trump_tweets.csv")

        # set new last tweet id
        last_tweet_id = tweets_list[-1].id


        # Repeat fetching tweets till total number of tweets 
        while len(tweets_list) < self.total_num_tweets:

            for i in range(0, 10):
                data = self.get_timeline_tweets(max_id=last_tweet_id)

                for tweet in data:
                    tweets_list.append(tweet)

                df = tweets_to_df(data)
                # Write to csv file
                df.to_csv("trump_tweets.csv", mode="a", header=False)
                last_tweet_id = tweets_list[-1].id

                print(
                    f"Wrote {len(df)} to file. Total number of fetched tweets: {len(tweets_list)}")

            # wait to not extend rate limits from Twitter API
            # because there is only a specific amount of requests you can 
            # make per time window
            time.sleep(6)


if __name__ == "__main__":

    # total number of tweets which should get fetched
    total_num_tweets = 10000
    client = TwitterCli(twitter_user="realDonaldTrump")

    # Fetch tweets and write to file
    client.get_tweet_collection(total_num_tweets)

    # print(dir(tweets[0]))
