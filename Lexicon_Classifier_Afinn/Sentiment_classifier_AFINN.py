__author__ = 'Padraig'

#!/usr/bin/python


import math
import re
import sys
import json
import simplejson
reload(sys)
sys.setdefaultencoding('utf-8')

# AFINN-111 is as of June 2011 the most recent version of AFINN
filenameAFINN = 'data/AFINN-111.txt'
afinn = dict(map(lambda (w, s): (w, int(s)), [
            ws.strip().split('\t') for ws in open(filenameAFINN) ]))

# Word splitter pattern
pattern_split = re.compile(r"\W+")

def sentiment(text):
    """
    Returns a float for sentiment strength based on the input text.
    Positive values are positive valence, negative value are negative valence.
    """
    words = pattern_split.split(text.lower())
    sentiments = map(lambda word: afinn.get(word, 0), words)
    if sentiments:
        # How should you weight the individual word sentiments?
        # You could do N, sqrt(N) or 1 for example. Here I use sqrt(N)
        sentiment = float(sum(sentiments))/math.sqrt(len(sentiments))

    else:
        sentiment = 0
    return sentiment



if __name__ == '__main__':
    # Single sentence example:
    text = "School is so boring"
    print("%6.2f %s" % (sentiment(text), text))

    # No negation and booster words handled in this approach
    text = "My school is the best school in wicklow i love it"
    print("%6.2f %s" % (sentiment(text), text))

    text = "have like no spots for the whole of summer then right before school, bam "
    print("%6.2f %s" % (sentiment(text), text))

    text = "saw my favourite teacher from school today i love you rosie "
    print("%6.2f %s" % (sentiment(text), text))

    text = "i always turn my alarms off in my sleep and no one woke me up so now i have to stay at home and miss school "
    print("%6.2f %s" % (sentiment(text), text))

    text = "went to school for an hour today and it sucked so bad "
    print("%6.2f %s" % (sentiment(text), text))

    text = "back to school tomorrow cant wait so excited to see my friends "
    print("%6.2f %s" % (sentiment(text), text))

    text = "Between -5 and plus 5 sentiment analysis "
    print(text)


