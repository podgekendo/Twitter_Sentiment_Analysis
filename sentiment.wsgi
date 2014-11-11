__author__ = 'Padraig'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#wsgi is a simple interface between web servers and web application for Python
# Has 2 sides the server/ gateway and the app/framework. To process a wsgi request the server side provides enviro
# information and a callback function to the app side. app process the request and returns a response
# Implements both sides of the API, can intermediate between a server and a app.
# Was originally working with Apache however I couldnt change the http.conf on the csi server

# handy functions to parse raw requests
from cgi import parse_qs, escape

# Manipulate csvs
import csv
import os
# regular expressions
import re
import sys
import time

# Import NLTK to do natural language processing
# Import the NLTK Classifiers

import nltk
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import LinearSVC
from nltk.classify.naivebayes import NaiveBayesClassifier

# had to import local modules like models, session_manager
# the same can be done with WSGIPythonPath directive in apache config
DIR_PATH = os.path.dirname(__file__)
if DIR_PATH not in sys.path:
    sys.path.append(DIR_PATH)

# model of Sentiment object in DB
from models import Sentiment
from session_manager import SessionManager

# ========================== python logging config =============================
import logging

# message format in log
FORMATTER = logging.Formatter(
      fmt='%(asctime)s [%(levelname)s]: %(message)s'
    , datefmt='%d/%m/%Y %H:%M:%S'
)

log_filename = DIR_PATH + os.path.sep + 'spam.log'

# 'a' - append mode
spam_h = logging.FileHandler(
      filename=log_filename
    , mode='a'
    , encoding='utf-8'
)
spam_h.setLevel(logging.DEBUG)
spam_h.setFormatter(FORMATTER)


logger = logging.getLogger('sent')
logger.addHandler(spam_h)
# ======================== end of logging config  =========================

# kind of global config section
TRAINING_SET_PATH = os.path.join(DIR_PATH, 'static/train.csv')
TEMPLATE_FILENAME = os.path.join(DIR_PATH, 'template.html')

class Classifier(object):
    """Classifier, which can predict the sentiment of tweets."""
    def __init__(self, training_set_path=None):
        super(Classifier, self).__init__()

        if not training_set_path:
            global TRAINING_SET_PATH
            self.TRAINING_SET_PATH = TRAINING_SET_PATH
        else:
            self.TRAINING_SET_PATH = training_set_path

        self.train_classifier()

    def train_classifier(self):
        """ Training procedure of classifier"""
        pos_tweets = []
        neg_tweets = []

        if not os.path.exists(self.TRAINING_SET_PATH):
            logger.error("Training set path is not set!"\
                         "Can't train classifier!")
            self.classifier = None
            return

        f = open(self.TRAINING_SET_PATH, 'rb')
        raw_tweets = csv.reader(f, delimiter=',')

        tweets = []
        for row in raw_tweets:
            sentiment = row[0]
            # The datetime information of the tweet was included, but I ignored it.
            tweet = row[1]
            item = (tweet, sentiment)
            tweets.append(item)
            if sentiment == "positive":
                pos_tweets += item
            else:
                neg_tweets += item
        f.close()

               # Split the data into training and test data
               # calculate the cutoff for each category
        negcutoff, poscutoff = len(neg_tweets) * 4 / 5, len(pos_tweets) * 4 / 5
               # set the train-feats and test feats accordingly
        pos_train, pos_test = pos_tweets[:poscutoff], pos_tweets[poscutoff:]
        neg_train, neg_test = neg_tweets[:negcutoff], neg_tweets[negcutoff:]

        neg_feats_train = self.get_train_features_from_tweets(neg_train, 'neg')
        pos_feats_train = self.get_train_features_from_tweets(pos_train, 'pos')

        train_feats = neg_feats_train + pos_feats_train

        self.classifier = SklearnClassifier(LinearSVC())
        self.classifier.train(train_feats)

#tokenizing, filtering and cleaning methods

    def process_tweet(tweet):
        # Convert to lower case
        tweet = tweet.lower()
        # Convert www.* or https?://* to URL
        tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))', 'URL', tweet)
        # Convert @username to AT_USER
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
        # Remove additional white spaces
        tweet = re.sub('[\s]+', ' ', tweet)
        # Replace #word with word
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        # Trim quotes
        tweet = tweet.strip('\'"')
        return tweet

        # Takes a tweet as input and returns the feature set
    def get_features_from_tweet(tweet):
        # Tokenizes the tweet into a list of words
        tokens = process_tweet(tweet).split()
        return dict((w, True) for w in tokens)

        #Compiles the training features form a list of tweets and how they were classified
    def get_train_features_from_tweets(tweets, pos_neg):
        tweet_features = []
        for tweet in tweets:
            features = get_features_from_tweet(tweet)
            tweet_features.append((features, pos_neg))
        return tweet_features

        # Load the data in and
        # Sort the tweets that were labelled "pos" and "neg"
    def make_prediction(self, prediction_tweet):
        if not prediction_tweet:
            return 'No prediction for empty tweet'
        if not self.classifier:
            logger.error("Classifier isn't trained!")
            return 'Error! Classifier is not trained!'
        prediction_features = self.get_features_from_tweet(prediction_tweet)
        return self.classifier.classify(prediction_features)

def _get_db_session():
    """ Acquire db session"""
    try:
        sm = SessionManager()
        session = sm.createNewSession()
    except Exception as e:
        session = None
        logger.exception('Can not acquire db session!')
    return session


def write_to_db(session, tweet_, sentiment_):
    """ Create db object (row in the db table) and write
        it into db using opened session.
    """
    if (not session) or (not tweet_) or (not sentiment_):
        logger.warn("Empty parameter! Can't write to DB!")
        return False

    db_obj = Sentiment(timestamp=time.time()
                       , tweet=tweet_
                       , sentiment=sentiment_
    )
    session.add(db_obj)
    session.commit()
    return True

import random
from tweepy import API, OAuthHandler
from auth import TwitterAuth


def predict_similar_tweets(classifier, tweet):
    if not tweet:
        return None

    hashtag_re = '#\w+'
    hashtags = re.findall(hashtag_re, tweet)
    if hashtags:
        # choose random hashtag, for more than 1
        search_term = random.choice(hashtags)
    else:
        # choose words with length > 3 letters
        words = [ word for word in tweet.split() if len(word) > 3 ]
        # if all words are short ones, choose random
        words = words or tweet.split()
        search_term = random.choice(words)

    search_response = None
    # using twitter search api
    try:
        auth = OAuthHandler(TwitterAuth.consumer_key, TwitterAuth.consumer_secret)
        auth.set_access_token(TwitterAuth.access_token, TwitterAuth.access_token_secret)
        api = API(auth, timeout=20)
        search_response = api.search(search_term, lang='en', rpp=20)

    except Exception as e:
        logger.exception('[-] Error, while using tweepy!')
        return '[-] Error, while searching similar tweets!'

    # compose colored list of tweets and predictions
    list_html = """
    <ul class="list-group">
      %s
    </ul>
    """
    lines = ''
    pos_template = '\t<li class="list-group-item list-group-item-success">%s</li>\n'
    neg_template = '\t<li class="list-group-item list-group-item-danger">%s</li>\n'
    for s in search_response:
        prediction = classifier.make_prediction(s.text)
        tweet_ = '<strong>@%s</strong>: %s' % (s.author.name, s.text)
        if prediction == 'pos':
            line = pos_template % tweet_
        else:
            line = neg_template % tweet_
        lines += line
    result = '<h4><p class="text-center">Search term is: <strong>%s</strong></p></h4>' % search_term
    result += list_html % lines

    # don't show any non-ascii symbols
    return result.encode('ascii', errors='ignore')


def form_response_body(tweet, sentiment, similar_predictions):
    # compose response body.
    # HTML template is in separate file.
    # Template made using simple html form and twitter bootstrap css
    # http://getbootstrap.com/css/#forms (documentation)
    response_body = ''
    try:
        with open(TEMPLATE_FILENAME, 'rb') as f:
            # read template from file
            html = f.read()
            # insert parameters into html template
            # instead of '%s' format strings in template.html
            response_body = html % (tweet or 'Empty'
                                  , sentiment or 'No prediction'
                                  , similar_predictions or ''
            )
    except IOError as e:
        logger.exception('Template reading error!')
        response_body = str(e)

    return response_body

# WSGI requires presense of *main* callable named 'application' 2 parameters environ and start_response
def application_(environ, start_response):
    # environ dictionary containing enviroment variables in CGI.
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)

    tweet = None
    sentiment = None
    similar_predictions = None

    d = parse_qs(request_body)
    if d:
        tweet = d.get('tweet', '')[0]

    if tweet:
        # Escape user input to avoid script injection
        tweet = escape(tweet)

        # create classifier instance
        classifier = Classifier()
        # predict sentiment
        sentiment = classifier.make_prediction(tweet)

        similar_predictions = predict_similar_tweets(classifier, tweet)


         # write some stats into DB
         session = _get_db_session()
         write_to_db(session, tweet, sentiment)

    response_body = form_response_body(tweet, sentiment, similar_predictions)

    # HTTP response code and message
    status = '200 OK'

    # These are HTTP headers expected by the client (browser)
    # They must be wrapped as a list of tupled pairs:
    # [(Header name, Header value)]
    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_body)))]

    # Send them to the server using the supplied function
    start_response(status, response_headers)

    # Return the response body
    # Notice it is wrapped in a list although it could be any iterable
    return [response_body]


# wrapper around application_ to provide exception handler for
# any unknown exceptions
def application(environ, start_response):

    response_iterable = application_(environ, start_response)
    return response_iterable

httpd = make_server(
    'localhost', # The host name.
    8081, # A port number where to wait for the request.
    application # Our application object name, in this case a function.
    )

# Wait for a single request, serve it and quit.
httpd.serve_forever()
