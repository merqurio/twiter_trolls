import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from collections import Counter

# Check the corpora is installed
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')


def tweet_stemming(tweet, token_freqs):

    """
    Stems tweets words and counts diversty
    
    :param tweet: the tweet to analyze
    :type tweet: str or unicode

    :param token_freqs: counter of words frequency
    :type token_freqs: Counter

    :returns: words added to token_freqs
    :rtype: int
    """
    
    pattern_url = '((https?:\/\/)|www\.)([\da-z\.-]+)\.([\/\w \.-]*)( |$)'
    regex_punctuation = re.compile('[%s]' % re.escape(string.punctuation))
    porter = PorterStemmer()

    counter_tokens = 0
    tweet_url_removed = re.sub(pattern_url, '', tweet, flags=re.MULTILINE)  # remove URL
    tweet_url_removed_tokenized = word_tokenize(tweet_url_removed)  # tokenize tweet
    tweet_url_removed_tokenized_cleaned_stemming = []  # cleaned of URLs and hashs, and stemming

    for token in tweet_url_removed_tokenized:
        new_token = regex_punctuation.sub(u'', token)  # remove punctuation and hash
        if not new_token == u'':
            new_token_stemming = porter.stem(new_token)
            tweet_url_removed_tokenized_cleaned_stemming.append(new_token_stemming)
            token_freqs[new_token_stemming] += 1
            counter_tokens += 1
    
    return counter_tokens


def tweet_hashtags(hashtags, hashtag_freqs):

    """
    Looks for hashtags and counts diversty
    
    :param hashtags: the list of hashtags to analyze
    :type hashtags: list

    :param hashtag_freqs: counter of hashtags frequency
    :type hashtag_freqs: Counter

    :returns: hashtags added to hashtag_freqs
    :rtype: int
    """
    
    for hashtag in hashtags:
        hashtag_freqs[hashtag['text']] += 1
    return len(hashtags)


def tweet_iteration_stemming(user):
    """
    For a given user, returns its ratio of tweets language diversity,
    between 0 and 1 (0: low diversity, 1: high diversity)
    or -1 if no word is used in tweets
    
    :param user: json of the user
    :type user: json

    :returns: ratio of tweets language diversity
    :rtype: float
    """
    
    tweets = user['tweets']
    token_freqs = Counter()
    counter_tokens = 0
    
    for tweet in tweets:
        if tweet["lang"] == "en":
            counter_tokens += tweet_stemming(tweet['text'], token_freqs)
        
    if( counter_tokens == 0 ):
        return -1
    else:
        token_diversity_ratio = float(len(token_freqs))/counter_tokens
        return token_diversity_ratio


def tweet_iteration_hashtags(user):

    """
    For a given user, returns its ratio of hashtags diversity,
    between 0 and 1 (0: low diversity, 1: high diversity), 
    or -1 if no hashtag is used
    
    :param user: json of the user
    :type user: bson

    :returns: ratio of hashtags diversity
    :rtype: float
    """

    if user["tweets_with_hashtags"] <= 0:
        return -1
    
    tweets = user["tweets"]
    hashtag_freqs = Counter()
    counter_hashtags = 0
    
    for tweet in tweets:
        hashtags = tweet['entities']["hashtags"]
        if len(hashtags) > 0:
            counter_hashtags += tweet_hashtags(hashtags, hashtag_freqs)

    hashtag_diversity_ratio = float(len(hashtag_freqs))/counter_hashtags
    
    return hashtag_diversity_ratio


def tweet_iteration_urls(user):
    """
    For a given user, returns the percentage of tweets with urls
    
    :param user: json of the user
    :type user: json

    :returns: percentage of tweets with urls
    :rtype: float
    """
    
    tweets = user['tweets']
    counter_tweets = 0
    counter_urls = 0
    
    for tweet in tweets:
        counter_tweets += 1
        urls =  len(tweet["entities"]["urls"])
        if urls != 0:
            counter_urls += 1

    urls_percentage = float(counter_urls)*100/counter_tweets
    
    return urls_percentage


def percentage_spammer(diversity_tweets, diversity_hashtags, urls_percentage):
    if diversity_tweets == -1:
        return 0
    if diversity_hashtags == -1:
        return 90*(1-diversity_tweets)
    return float(600*(1-diversity_tweets)+150*(1-diversity_hashtags)+2.5*urls_percentage) / 10