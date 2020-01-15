"""
author: @climatebrad
"""
import string
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, classification_report

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
            self.split_articles['X_train'] = articleVectorizer.fit_transform(self.split_articles['X_train'].body_text)
            self.split_articles['X_test'] = articleVectorizer.transform(self.split_articles['X_test'].body_text)
            all_vect = articleVectorizer.transform(articles_df.pop('body_text'))
        else:
            all_vect = articleVectorizer.fit_transform(articles_df.pop('body_text'))

        for i, col in enumerate(articleVectorizer.get_feature_names()):
            articles_df[col] = pd.Series(all_vect[:, i].toarray().ravel())
        self._vectorized_articles = articles_df
        return articles_df
        
    @staticmethod
    def train_test_split(X, y, random_state=42, test_size=0.2):
        """generate train-test split"""
        split = {}
        (split['X_train'], split['X_test'], 
         split['y_train'], split['y_test']) = train_test_split(X, y,
                                                               random_state=random_state,
                                                               stratify=y,
                                                               test_size=test_size)
        return split


    def train_test_split_articles(self, random_state=42, test_size=0.2):
        """train-test-split articles"""       
        X = pd.DataFrame(self.articles.body_text)
        y = self.articles.cluster
        self._split_articles = self.train_test_split(X, y, random_state, test_size)
        return self.split_articles

    def resample_articles(self, mode='SMOTE', random_state=42):
        """Resample articles to deal with majority class.
        mode can be SMOTE, undersample"""
        if mode == 'SMOTE':
            smote = SMOTE(random_state=random_state)
            (self.split_articles['X_train_resampled'], 
             self.split_articles['y_train_resampled']) = smote.fit_sample(self.split_articles['X_train'], 
                                                                        self.split_articles['y_train']) 
        elif mode == 'undersample':
            rus = RandomUnderSampler('majority', random_state=random_state)
            (self.split_articles['X_train_resampled'], 
             self.split_articles['y_train_resampled']) = rus.fit_resample(self.split_articles['X_train'], 
                                                                        self.split_articles['y_train']) 
        elif mode == 'oversample':
            raise Exception("mode must be 'SMOTE' or 'undersample'")


    def train_article_classifier(self, classifier='LogisticRegression', resampled=True, **params):
        """Fit classifier to training articles.
        Fit to resampled training data if resampled=True"""
        default_params = {
            'solver' : 'saga',
            'multi_class' : 'multinomial',
            'penalty' : 'l1',
            'random_state' : 42,
            'max_iter' : 1000,
            'C' : 0.1,
            'n_jobs' : -1,
        }
        params = {key : params.get(key, value) for key, value in default_params.items()}  
        print(f"Training {classifier} classifier with params {params}...")
        self._classifier = LogisticRegression(**params)
        if resampled:
            if 'X_train_resampled' not in self.split_articles:
                raise Exception('Resampled data does not exist. Run Modeler.resample_articles().')
            X_train, y_train = self.split_articles['X_train_resampled'], self.split_articles['y_train_resampled']
        else:
            X_train, y_train = self.split_articles['X_train'], self.split_articles['Y_train']
        self.classifier.fit(X_train, y_train)
        
    def display_classifier_accuracy(self, display_train=False, target_names=None):
        """Print out accuracy and density of results.
        if display_train=True, show results for training set"""
        if display_train:
            y_pred = self.classifier.predict(self.split_articles['X_train'])
            y_test = self.split_articles['y_train']
            which = 'Train'
        else:
            y_pred = self.classifier.predict(self.split_articles['X_test'])
            y_test = self.split_articles['y_test']
            which = 'Test'
        accuracy = accuracy_score(y_test, y_pred)
        density = np.mean(self.classifier.coef_ != 0, axis=1) * 100
        print(f'{which} accuracy: {accuracy:.4f}')
        print('%% non-zero coefficients per class:\n %s' % (density))
        print(classification_report(y_test, y_pred, target_names=target_names))