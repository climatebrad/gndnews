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
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE

class ModelingMixin():
    """Modeling routines"""
    
    @property
    def vectorized_articles(self):
        """vectorized articles"""
        if self._vectorized_articles is None:
            raise Exception("Articles have not been vectorized. Run Modeler.vectorize_articles().")
        return self._vectorized_articles
    
    @property
    def split_articles(self):
        """train-test split articles"""
        if self._split_articles is None:
            raise Exception("Articles have not been split. Run Modeler.train_test_split_articles().")
        return self._split_articles

    @property
    def classifier(self):
        """classifier model"""
        if self._classifier is None:
            raise Exception("Classifer is not defined. Run Modeler.train_article_classifier().")
        return self._classifier  
    
    @classifier.setter
    def classifier(self, model):
        self._classifier = model
        
    def vectorize_articles(self, vectorizer='tfidf', split=True, **params):
        """generate vectorized tokens from article body_text. 
        vectorizer can be 'tfidf' or 'count'
        If split is true then fits on self.split_articles['X_train']"""
        if split and ((self.split_articles is None) or (self.split_articles.get('X_train') is None)):
            raise Exception("Articles have not been split. Run Modeler.train_test_split_articles().")
            
        articles_df = pd.DataFrame(self.articles.body_text.copy())
        stopwords_list = stopwords.words('english') + list(string.punctuation) + ["''", '""', '...', '``','’','“','”']

        if vectorizer == 'tfidf':
            articleVectorizer = TfidfVectorizer(stop_words=stopwords_list, **params)
        else:
            articleVectorizer = CountVectorizer(stop_words=stopwords_list, **params)

        if split:
            self.split_articles['X_train'] = articleVectorizer.fit_transform(self.split_articles.get('X_train'))
            self.split_articles['X_test'] = articleVectorizer.transform(self.split_articles.get('X_test'))
            all_vect = articleVectorizer.transform(articles_df.pop('body_text'))
        else:
            all_vect = articleVectorizer.fit_transform(articles_df.pop('body_text'))
        
        for i, col in enumerate(vect.get_feature_names()):
            articles_df[col] = pd.Series(all_vect[:, i].toarray().ravel())
        self._vectorized_articles = articles_df
        return articles_df
        
    @staticmethod
    def train_test_split(X, y, random_state=42, test_size=0.2):
        """generate train-test split"""
        split = {}
        split['X_train'], split['X_test'], 
        split['y_train'], split['y_test'] = train_test_split(X, y,
                                                             random_state=42,
                                                             stratify=y,
                                                             test_size=0.2)
        return split
        
        
    def train_test_split_articles(self, random_state=42, test_size=0.2):
        """train-test-split articles"""       
        X = pd.DataFrame(self.articles.body_text)
        y = self.articles.cluster
        self._split_articles = self.test_train_split(X, y, random_state, test_size)
        return self.split_articles
    
    def resample_articles(self, mode='SMOTE', random_state=42):
        """Resample articles to deal with majority class.
        mode can be SMOTE, undersample"""
        if mode == 'SMOTE' :
            smote = SMOTE(random_state=42)
            self.split_articles['X_train_resampled'], 
            self.split_articles['y_train_resampled'] = smote.fit_sample(self.split_articles['X_train'], 
                                                                        self.split_articles['y_train']) 
        elif mode == 'undersample':
            rus = RandomUnderSampler(random_state=0)
            self.split_articles['X_train_resampled'], 
            self.split_articles['y_train_resampled'] = rus.fit_resample(self.split_articles['X_train'], 
                                                                        self.split_articles['y_train']) 
        else:
            raise Exception("mode must be 'SMOTE' or 'undersample'")


    def train_article_classifier(self, classifier='LogisticRegression', resampled=True, **params):
        """Fit classifier to training articles.
        Fit to resampled training data if resampled=True"""
        if params == {}:
            params = {
                'solver' : 'saga',
                'multi_class' : 'multinomial',
                'penalty' : 'l1',
                'random_state' : 42,
                'max_iter' : 1000,
                'C' : 0.1,
            }
        self._classifier = LogisticRegression(**params)
        print(f"Training {classifier} classifier with params {params}...")
        if resampled:
            if not self.split_articles.get('X_train_resampled'):
                raise Exception('Resampled data does not exist. Run Modeler.resample_articles().')
            X_train, y_train = self.split_articles['X_train_resampled'], self.split_articles['y_train_resampled']
        else:
            X_train, y_train = self.split_articles['X_train'], self.split_articles['Y_train']
        self.classifier.fit(X_train, y_train)
        
        
        