"""
author: @climatebrad
"""
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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class ModelingMixin():
    """Modeling routines"""
    
    @property
    def vectorized_articles(self):
        """vectorized articles"""
        if self._vectorized_articles is None:
            raise Exception("Articles have not been vectorized. Run Modeler.vectorize_articles().")
        return self._vectorized_articles

    def vectorize_articles(self, vectorizer='tfidf', **params):
        """generate vectorized tokens from article body_text. 
        vectorizer can be 'tfidf' or 'count'"""
        articles_df = pd.DataFrame(self.articles.body_text.copy())
        stopwords_list = stopwords.words('english') + list(string.punctuation) + ["''", '""', '...', '``','’','“','”']
        if vectorizer == 'tfidf':
            articleVectorizer = TfidfVectorizer(stop_words=stopwords_list, **params)
        else:
            articleVectorizer = CountVectorizer(stop_words=stopwords_list, **params)

        X = articleVectorizer.fit_transform(articles_df.pop('body_text'))
        for i, col in enumerate(vect.get_feature_names()):
            articles_df[col] = pd.Series(X[:, i].toarray().ravel())
        self._vectorized_articles = articles_df
        return articles_df
        
    def test_train_split(self, X, y, random_state=42, test_size=0.2):
        """generate test-train split"""
        
    def test_train_split_articles(self, random_state=42, test_size=0.2):
        """test-train split vectorized articles"""
        X = self.vectorized_articles
        y = self.articles.cluster
        
    def train_article_classifier(self, classifier='LogisticRegression'):
        """"""
        lr = LogisticRegression(solver='saga',
                        multi_class='multinomial',
                        penalty='l1',
                        random_state=42,
                        max_iter=1000,
                        )
        lr.fit(X_train, y_train)
        
        
        