__author__ = 'Padraig'
from pymongo import Connection
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime

# My MongoDB connection info. MY database name is TwitterStream, and my collection is tweets.
connection = Connection('localhost', 27017)
db = connection.TwitterStream
db.tweets.ensure_index("id", unique=True, dropDups=True)
collection = db.tweets

# The keywords I wanted to track, used a variety of cashtags, hashtags, and words.
keywords = ['$school', '#college', 'summer']

# Only grab tweets of a specific language, in this case I wanted english
language = ['en']

# Oauth keys from twitter
consumer_key = "SHkACtUGX5NU6TGXiQ35qno9Z"
consumer_secret = "ve4z06HW7WOhhczo5qSMqDCRooCrBYPrNvhZPthFWqIUkKpklw"
access_token = "385580060-2X0OdgsJKujR5prW9fuosUHulZ1mnI8vo0i1kTGQ"
access_token_secret = "4uLJ4x0mieqaYCpdVBwaTqIVmTOJ25CBx4FC9foRG1Bls"

# The below code will get Tweets from the stream and store only the important fields to my database
class StdOutListener(StreamListener):

    def on_data(self, data):

        # Load the Tweet into the variable "t"
        t = json.loads(data)

        # Pull important data from the tweet to store in the database.
        tweet_id = t['id_str']  # The Tweet ID from Twitter in string format
        username = t['user']['screen_name']  # The username of the Tweet author
        followers = t['user']['followers_count']  # The number of followers the Tweet author has
        text = t['text']  # The entire body of the Tweet
        hashtags = t['entities']['hashtags']  # Any hashtags used in the Tweet
        dt = t['created_at']  # The timestamp of when the Tweet was created
        language = t['lang']  # The language of the Tweet

        # Convert the timestamp string given by Twitter to a date object called "created". This is more easily manipulated in MongoDB.
        created = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

        # Load all of the extracted Tweet data into the variable "tweet" that will be stored into the database
        tweet = {'id':tweet_id, 'username':username, 'followers':followers, 'text':text, 'hashtags':hashtags, 'language':language, 'created':created}

        # Save the refined Tweet data to MongoDB
        collection.save(tweet)

        # Print the username and text of each Tweet to my console in realtime as they are pulled from the stream while saving them also to the database
        print username + ':' + ' ' + text
        return True

    # Prints the reason for an error if one to my console
    def on_error(self, status):
        print status

# Some Tweepy code that pulls from variables at the top of the script
if __name__ == '__main__':
	try:
		#Create a file to store output. "a" means append (add on to previous file)
		fhOut = open("data\output.csv","a") """ may need to be saved as output.json then changed to output.json manually in notepad. Python sometimes issues saving as .csv"""

		l = StdOutListener()
		auth = OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		stream = Stream(auth, l)
		stream.filter(track=keywords, languages=language)
		
	except KeyboardInterrupt:
		#User pressed ctrl+c -- get ready to exit the program
		pass

	#Close the
	fhOut.close()
