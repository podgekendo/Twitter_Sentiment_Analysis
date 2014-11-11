#Sentiment Classification using NLTK, & Naive Bayes Classifiers

##3rd party libs, required to run the app:

*sqlalchemy*nltk http://www.nltk.org *scikits-learn and its' dependensies (numpy, scipy, ...) http://numpy.scipy.org*apache(originally)*python application server 'wsgiref'(now)  https://docs.python.org/2/library/wsgiref.html*mod_wsgi*sentiwordNEt  http://sentiwordnet.isti.cnr.it*


###Files:

```
sentiment.wsgi -	 My main python script integrated my sentiment_analysis.py file aswell as my pre_process.py file. It contains function named 'application' in accordance of wsgi *interface*.
static/train.csv -	 Consists of the Sanders Corpus of tagged tweets which were used as a training set for the classifier
template.html  - 	 Is my html form, with twitter bootstrap integrated into it to add a touch of colour. 
models.py      - 	 Declaration of my sentiment db object in sql-alchemy format. Worked best with amazon servers. and Wsgi web applications. (Web service gateway interfaces) The type of wsgi I used is Wsgi_ref a simple server form.
session_manager.py - Works as a helper class. It contains DB configuration, connects to the DB and returns session object.
schema_manager.py  - Not explicitly used anywhere. But it used servers to create and drop db schema.
twitter_mongodb.py - My python script that uses the Tweepy library to pull Tweets with specific keywords from Twitter's Streaming API, and then stores the important fields from the Tweet in my MongoDB collection. I used mongodb for saving the live twitter feed as its much easier to handle when dealing with large amounts of tweets, much faster and stores in a json style rather then have to create rows columns etc.
pre_process.py - When I run my twitter_to_mongo.py a output.json file is created of the tweets streamed from the twitter api which I run through the preprocesser to tidy up before sending to the sentiment_analysis.py
sentiment_analysis.py - analyzes the large feed of data and returns a sentiment value for each tweet.
Sentiment_classifier_AFINN.py - An example of a lexicon based classifier that I used to test against my own.
data/ - train.csv : Consists of the Sanders Corpus of tagged tweets which were used for training the classifier.  It consists of 5513 hand-classified tweets. 
output.csv: which is the processed tweets from the live feed on the keywords ‘school’, ‘university’ and ‘education’ which was used to test the trained classifier
Stopwords file: which contains words which  are unnecessary noise in deciding sentiment
AFFINN-111.text: which is the dictionary of words rated for sentiment between -5 and +5.
```

####Web Application
The app is built using wsgi interface
e.g http://webpython.codepoint.net/wsgi_application_interface

#####Deployment Examples
Deployed on amazon instance with server Ubuntu installed on it. 
Apache server with  mod_wsgi module is used as Web server.
Apache configuration listed in httpd.conf file, which usually located on file system here: /etc/apache2/httpd.conf.



