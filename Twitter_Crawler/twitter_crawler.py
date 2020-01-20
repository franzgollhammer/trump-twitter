from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import datetime
import time


##### CONSTANTS #####

# Path to chrome browser-driver executable
CHROME_DRIVER_PATH = "./chromedriver"

# Scroll pause time for selenium
SCROLL_PAUSE_TIME = 0.5

# Lists with dates for crawling
# i.e. from Jan. 1st
#      to   Jan. 15th

DATE_LIST = [
    "01-01", "01-15", "01-16", "01-31", "02-01", "02-15", "02-16", "02-28",
    "03-01", "03-15", "03-16", "03-31", "04-01", "04-15", "04-16", "04-30",
    "05-01", "05-15", "05-16", "05-31", "06-01", "06-15", "06-16", "06-30",
    "07-01", "07-15", "07-16", "07-31", "08-01", "08-15", "08-16", "08-31",
    "09-01", "09-15", "09-16", "09-30", "10-01", "10-15", "10-16", "10-31",
    "11-01", "11-15", "11-16", "11-30", "12-01", "12-15", "12-16", "12-31",
]

YEAR_LIST = [
    "2015", "2016", "2017", "2018", "2019"
]

##### MAIN ####


def get_tweets_from_url(url):
    """ Get all tweets from twitter search url with format:
    "https://twitter.com/search?f=tweets&vertical=default&q=from%3Arealdonaldtrump%20since%3A{year}-{DATE_LIST[i]}%20until%3A{year}-{DATE_LIST[i+1]}include%3Aretweets&src=typd"
    """
    # Open browser with URL
    browser.get(url)

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get page source code
    source_code = browser.page_source

    # Parse source coude with beautifulsoup4
    soup = BeautifulSoup(source_code, "html.parser")

    ### EXTRACT DATA ###

    # FIXME: Refactor to on loop and build DS / DF ?
    # Fetch one tweet and extract ["likes"], ["comments"], ["retweets"]

    # TODO: !!!! MAKE IT HAPPEN !!!! 
    # Extract whole tweets as data

    _tweets = [tweet for tweet in soup.find_all("div", class_="tweet")]
    for tweet in _tweets:
        deb = tweet.find_all("p", class_="tweet_text")
        debug_text = [text for text in tweet.find_all("p", class_="tweet_text")][0].text
        debug_date = [date for date in tweet.find_all("span", class_="_timestamp")][0].text
        print(dir(debug_date))
        x = 5

    # Extract tweet texts
    tweet_texts = []
    for tweet_text in soup.find_all("p", class_="tweet-text"):
        text = tweet_text.get_text()
        tweet_texts.append(text)

    # Extract tweet date
    tweet_dates = []
    for span in soup.find_all("span", class_="_timestamp"):
        # Convert seconds to timestamp
        span_date = span["data-time"]
        date = str(datetime.datetime.fromtimestamp(int(span_date)).isoformat())
        tweet_dates.append(date)

    # Extract number of likes
    num_tweet_likes = []
    print("Likes: ", soup.find_all("button", class_="js-actionFavorite"))
    for button in soup.find_all("button", class_="js-actionFavorite"):
        buttons = button.find_all(
            "span", class_="ProfileTweet-actionCountForPresentation")
        for b in buttons:
            num_tweet_likes.append(b.text)

    # Extract number of comments
    num_tweet_comments = []
    print("Comments: ", soup.find_all("button", class_="js-actionReply"))
    for button in soup.find_all("button", class_="js-actionReply"):
        buttons = button.find_all(
            "span", class_="ProfileTweet-actionCountForPresentation")
        for b in buttons:
            num_tweet_comments.append(b.text)

    # Extract number of retweets
    num_tweet_retweets = []  # js-actionRetweet
    print("Retweets: ", soup.find_all("button", class_="js-actionRetweet"))
    for button in soup.find_all("button", class_="js-actionRetweet"):
        buttons = button.find_all(
            "span", class_="ProfileTweet-actionCountForPresentation")
        for b in buttons:
            num_tweet_retweets.append(b.text)

    # Build tweet dictionary list from extracted data
    tweets = {
        "date": tweet_dates,
        "text": tweet_texts,
        "likes": num_tweet_likes,
        "comments": num_tweet_comments,
        "retweets": num_tweet_retweets
    }

    return tweets


if __name__ == "__main__":

    # Init chrome browser
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)

    # Init csv file
    csv_file = open("scrape_data.csv", "w")

    # Init csv writer and file
    csv_writer = csv.writer(csv_file)

    # Write headers to file
    csv_writer.writerow(["date", "text", "likes", "comments", "retweets"])

    for year in YEAR_LIST:
        for i in range(len(DATE_LIST) - 1):
            # URL with query string
            url = f"https://twitter.com/search?f=tweets&vertical=default&q=from%3Arealdonaldtrump%20since%3A{year}-{DATE_LIST[i]}%20until%3A{year}-{DATE_LIST[i+1]}include%3Aretweets&src=typd"

            # Get tweets from url
            tweets = get_tweets_from_url(url)

            # Write tweet data to csv file
            for j in range(len(tweets["date"])):
                csv_writer.writerow([
                    tweets["date"][j],
                    tweets["text"][j],
                    tweets["likes"][j],
                    tweets["comments"][j],
                    tweets["retweets"][j]
                ])

    # Close browser session for clean up
    browser.close()
