import re
import pymongo
import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
from nltk import word_tokenize, FreqDist
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer

class Modeler():
    """Modeling object"""
    def __init__(self):
        self._articles = None
        self._keywords = None
        self._vectorized_keywords = None
        self._k_means = None
        self._gizmodo_stop_words = None
        
    @property 
    def articles(self):
        """load articles into dataframe from mongodb"""
        if self._articles is None:
            myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
            mydb = myclient['items']
            mycollection = mydb['articles']
            articles = pd.DataFrame(list(mycollection.find({})))
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
            gizmodo_properties = ['earther',
                                  'gizmodo',
                                  'lifehacker',
                                  'the root',
                                  'jalopnik',
                                  'deadspin',
                                  'i09',
                                  'the takeout',
                                  'jezebel',
                                  'paleofuture',
                                  'gawker',
                                  'the slot',
                                  'kotaku',
                                  'the muse$',
                                  'the concourse',
                                  'the onion']
            regex = re.compile('('+'|'.join(gizmodo_properties)+')', re.IGNORECASE)
            keyword_list = set(self.keywords.sum()[0])
            self._gizmodo_stop_words = list(filter(regex.search, keyword_list))
        return self._gizmodo_stop_words
    
    @staticmethod
    def preprocess_token(token):
        """lowercase, replace spaces with underscore"""
        return token.replace(' ','_').lower()

    def vectorize_keywords(self, ignore_gizmodo=True, **params):
        """Return dataframe of vectorized self.keywords. 
        if ignore_gizmodo=True, stop_words include gizmodo properties.
        additional named params passed to CountVectorizer()"""
        stop_words = params.pop('stop_words',[])
        if ignore_gizmodo:
            stop_words.extend([self.preprocess_token(k) for k in self.gizmodo_stop_words])
        vect = CountVectorizer(stop_words=stop_words, **params)
        key_df = self.keywords.copy()
        X = vect.fit_transform(key_df.pop('keywords').map(lambda lst : ' '.join([self.preprocess_token(k) for k in lst])))
        for i, col in enumerate(vect.get_feature_names()):
            key_df[col] = pd.Series(X[:, i].toarray().ravel())
        self._vectorized_keywords = key_df
        return key_df
        
    @property
    def vectorized_keywords(self):
#        I think we should have to explicitly run self.vectorize_keywords()
        if self._vectorized_keywords is None:
            print("Keywords have not been vectorized. Run Modeler.vectorize_keywords().")
#            self._vectorized_keywords = self.vectorize_keywords()
        return self._vectorized_keywords
    
    @property
    def k_means(self):
        if self._k_means is None:
            print("k_means not defined. Run Modeler.cluster_keywords()")
        return self._k_means
    
    def cluster_keywords(self, n_clusters):
        """Run K-Means clustering on vectorized keywords, update articles.cluster column with predictions"""
        k_means = KMeans(n_clusters=n_clusters)
        k_means.fit(self.vectorized_keywords)
        self.articles['cluster'] = k_means.predict(self.vectorized_keywords)
        self._k_means = k_means
        return k_means


    def display_keyword_clusters(self, n_keywords=20, ignore_gizmodo=True):
        """Return dataframe of clusters with top n_keywords in descending order. 
        if ignore_gizmode=True, don't display keywords with gizmodo properties."""
        if 'cluster' not in self.articles:
            print("Clusters not defined. Run Modeler.cluster_keywords()")
            return
        clusters = {}
        for i in range(self.articles.cluster.max() + 1):
            cluster_kwds = self.articles[self.articles.cluster == i].keywords.sum()
            if ignore_gizmodo:
                cluster_kwds = [kwd for kwd in cluster_kwds if kwd not in self.gizmodo_stop_words]
            clusters[i] = (pd.Series(cluster_kwds)
                           .value_counts()
                           .head(n_keywords)
                           .reset_index()[['index',0]]
                           .apply(lambda x : x.astype(str))
                           .apply(" ".join, axis=1))
        return pd.DataFrame(clusters)