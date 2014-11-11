__author__ = 'Padraig'
#import regex
import re


"""start process_tweet"""
def processTweet(tweet):


    """Convert to lower case"""
    tweet = tweet.lower()
    """Convert www.* or https?://* to URL"""
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',tweet)
    """Convert @username to AT_USER"""
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    """Remove additional white spaces"""
    tweet = re.sub('[\s]+', ' ', tweet)
    """Replace #word with word"""
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    """trim2"""
    tweet = tweet.strip('\'"')
    return tweet
"""end"""

"""Read the tweets one by one and process it"""
""" should this not be output.csv """
fp = open('tweets.txt', 'r')
line = fp.readline()

while line:
    processedTweet = processTweet(line)
    print processedTweet
    line = fp.readline()#start process_tweet
def processTweet(tweet):
    # process the tweets

 """ If it preprocess'es them where does it saved the preprocessed """

#end loop
fp.close()
