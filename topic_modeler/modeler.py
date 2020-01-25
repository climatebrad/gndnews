import re
import os
import pymongo
from configparser import ConfigParser
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
from topic_modeler.newsifier import NewsifierMixin

class Modeler(NewsifierMixin, ModelingMixin, ClusteringMixin):
    """Modeling object"""
    # TODO - initialize with saved instance
    def __init__(self, settings_file='settings.ini'):
        self._settings_file = settings_file
        self._cfg = None
        self._articles = None
        self._keywords = None
        self._vectorized_keywords = None
        self._k_means = None
        self._gizmodo_stop_words = None
        self._mongo_collection = None
        self._vectorized_articles = None
        self._splitted_articles = None
        self._splitted_vectorized_articles = None
        self._article_vectorizer = None
        self._classifier = None
        self._cluster_names = None
        self._text_classifier = None
   
    @property 
    def cfg(self):
        if self._cfg is None:
            cfg = ConfigParser()
            cfg.read(self._settings_file)
            self._cfg = cfg
        return self._cfg

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
            # check if you're gcp
            if os.environ['HOME'] == '/home/jupyter':
                myclient = pymongo.MongoClient("mongodb+srv://dbUser:mbEBDyQyH5ltIfLf@cluster0-lqw4d.mongodb.net/test?retryWrites=true&w=majority")
            else:
                myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
            mongo_db = self.cfg['DB'].get('MONGO_DB', 'items')
            mydb = myclient[mongo_db]
            mongo_collection = self.cfg['DB'].get('MONGO_COLLECTION', 'items')
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
    
    @property 
    def gizmodo_sitenames(self):
        return list(map(lambda x: x.strip('$'), self.gizmodo_properties))