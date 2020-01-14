import re
import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA
import nltk
from nltk.corpus import stopwords
import string
from nltk import word_tokenize, FreqDist
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_samples, silhouette_score
from topic_modeler.clustering import ClusteringMixin
from topic_modeler.modeling import ModelingMixin

class Modeler(ModelingMixin, ClusteringMixin):
    """Modeling object"""
    def __init__(self):
        self._articles = None
        self._keywords = None
        self._vectorized_keywords = None
        self._k_means = None
        self._gizmodo_stop_words = None
        self._mongo_collection = None
        self._vectorized_articles = None
        self._split_articles = None
        self._classifier = None

    gizmodo_properties = {'earther' : 'environment',
                          'gizmodo' : 'general interest',
                          'lifehacker' : 'self-improvement',
                          'the root' : 'African-American',
                          'jalopnik' : 'cars',
                          'deadspin' : 'sports',
                          'i09' : 'nerd culture',
                          'the takeout' : 'food',
                          'jezebel' : 'feminism',
                          'paleofuture' : 'general interest',
                          'the slot' : 'feminist politics',
                          'kotaku' : 'video games',
                          'the muse$' : 'feminist culture',
                          'the concourse' : 'general interest',
                          'the onion' : 'satire'}
    
    gizmodo_regex = re.compile('(' + '|'.join(gizmodo_properties) + ')', re.IGNORECASE)
    
    @property
    def mongo_collection(self):
        if self._mongo_collection is None:
            myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
            mydb = myclient['items']
            self._mongo_collection = mydb['articles']
        return self._mongo_collection

    @property 
    def articles(self):
        if self._articles is None:
            articles = pd.DataFrame(list(self.mongo_collection.find({})))
            articles.created_at = pd.to_datetime(articles.created_at, infer_datetime_format=True)
            self._articles = articles
        return self._articles
    
    @property
    def keywords(self):
        """the keywords column from data into its own dataframe"""
        if self._keywords is None:
            self._keywords = pd.DataFrame(self.articles.keywords.copy())
        return self._keywords

    @property
    def gizmodo_stop_words(self):
        if self._gizmodo_stop_words is None:
            keyword_list = set(self.keywords.sum()[0])
            self._gizmodo_stop_words = list(filter(self.gizmodo_regex.search, keyword_list))
        return self._gizmodo_stop_words