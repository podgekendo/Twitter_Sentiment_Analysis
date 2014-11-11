__author__ = 'Padraig'
import csv
import re

from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import LinearSVC

""" Analyzes the large feed of data and returns a sentiment value for each tweet."""


def get_stop_word_list(stopWordListFileName):
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords

stopWords = get_stop_word_list('data\stopwords.txt')

#Already in my pre_process.py so unnecessary here
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


def get_features_from_tweet(tweet):
    tokens = process_tweet(tweet).split()
    return dict((w, True) for w in tokens)


def get_train_features_from_tweets(tweets, pos_neg):
    tweet_features = []
    for tweet in tweets:
        features = get_features_from_tweet(tweet)
        tweet_features.append((features, pos_neg))
    return tweet_features


pos_tweets = []
neg_tweets = []

raw_tweets = csv.reader(open('data\train.csv', 'rb'), delimiter=',')
tweets = []
for row in raw_tweets:
    sentiment = row[0]
    tweet = row[1]
    # processedTweet = process_tweet(tweet)
    # featureVector = getFeatureVector(processedTweet, stopWords)
    item = (tweet, sentiment)
    tweets.append(item)
    if sentiment == "positive":
        pos_tweets += item
    else:
        neg_tweets += item

negcutoff, poscutoff = len(neg_tweets) * 4 / 5, len(pos_tweets) * 4 / 5
pos_train, pos_test = pos_tweets[:poscutoff], pos_tweets[poscutoff:]
neg_train, neg_test = neg_tweets[:negcutoff], neg_tweets[negcutoff:]

neg_feats_train = get_train_features_from_tweets(neg_train, 'neg')
pos_feats_train = get_train_features_from_tweets(pos_train, 'pos')

train_feats = neg_feats_train + pos_feats_train

svm_classifier = SklearnClassifier(LinearSVC())
svm_classifier.train(train_feats)

# Evaluation
correct, wrong = 0, 0

for tweet in neg_test:
    features = get_features_from_tweet(tweet)
    result = svm_classifier.classify(features)
    if result == "neg":
        correct += 1
    else:
        wrong += 1


for tweet in pos_test:
    features = get_features_from_tweet(tweet)
    result = svm_classifier.classify(features)
    if result == "pos":
        correct += 1
    else:
        wrong += 1

print "Accuracy: {}".format(correct / float(correct + wrong))

"""The trained classifier is then tested on the newly acquired live feed data set"""

testTweet = open('data\output.csv', 'rb')
for item in testTweet:
    processedTestTweet = process_tweet(item)
    print item, svm_classifier.classify(get_features_from_tweet(processedTestTweet))