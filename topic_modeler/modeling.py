"""
author: @climatebrad
"""
import string
import numpy as np
import pandas as pd
import joblib
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC 
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline

class ModelingMixin():
    """Modeling routines"""

    @property
    def vectorized_articles(self):
        """vectorized articles"""
        if self._vectorized_articles is None:
            raise Exception("Articles have not been vectorized. Run Modeler.vectorize_articles(namify=True).")
        return self._vectorized_articles

    @property
    def splitted_articles(self):
        """train-test split articles"""
        if self._splitted_articles is None:
            raise Exception("Articles have not been split. Run Modeler.train_test_split_articles().")
        return self._splitted_articles
    
    @property
    def splitted_vectorized_articles(self):
        """train-test split articles"""
        if self._splitted_vectorized_articles is None:
            raise Exception("""Articles have not been split and vectorized. 
            Run Modeler.train_test_split_articles() then Modeler.vectorize_articles().""")
        return self._splitted_articles

    @property
    def article_vectorizer(self):
        """vectorizer"""
        if self._article_vectorizer is None:
            raise Exception("Vectorizer is not defined. Run Modeler.vectorize_articles().")
        return self._article_vectorizer
    
    @property
    def classifier(self):
        """classifier model"""
        if self._classifier is None:
            raise Exception("Classifer is not defined. Run Modeler.train_article_classifier().")
        return self._classifier

    @classifier.setter
    def classifier(self, model):
        self._classifier = model

    # we need to use sparse arrays directly here I think.
    def vectorize_articles(self, vectorizer='tfidf', gizmodo='ignore', split=True, namify=False, **params):
        """generate vectorized tokens from article body_text. 
        vectorizer can be 'tfidf' or 'count'
        If split is true then fits on self.splitted_articles['X_train']
        If namify is true then add vectorized words as named columns in self.vectorized_articles"""
        if split and ((self.splitted_articles is None) or (self.splitted_articles.get('X_train') is None)):
            raise Exception("Articles have not been split. Run Modeler.train_test_split_articles().")

        articles_df = pd.DataFrame(self.articles.body_text.copy())
        stop_words = stopwords.words('english') + list(string.punctuation) + ["''", '""', '...', '``','’','“','”']
        if gizmodo == 'ignore':
            stop_words.extend(self.gizmodo_sitenames)
        if vectorizer == 'tfidf':
            articleVectorizer = TfidfVectorizer(stop_words=stop_words, **params)
        else:
            articleVectorizer = CountVectorizer(stop_words=stop_words, **params)
        print("Vectorizing articles...")
        if split:
            self._splitted_vectorized_articles = {}
            # articleVectorizer.fit_transform returns a sparse matrix
            self.splitted_vectorized_articles['X_train'] = articleVectorizer.fit_transform(self.splitted_articles['X_train'].body_text)
            self.splitted_vectorized_articles['X_test'] = articleVectorizer.transform(self.splitted_articles['X_test'].body_text)
            all_vect = articleVectorizer.transform(articles_df.pop('body_text'))
        else:
            all_vect = articleVectorizer.fit_transform(articles_df.pop('body_text'))
        self._article_vectorizer = articleVectorizer
        # it's possible this is too memory intensive ? 
        if namify:
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
        self._splitted_articles = self.train_test_split(X, y, random_state, test_size)
        return self.splitted_articles

    def resample_articles(self, mode='SMOTE', random_state=42):
        """Resample articles to deal with majority class.
        mode can be SMOTE, undersample"""
        # SMOTE only works if smallest classes have enough samples
        if mode == 'SMOTE':
            smote = SMOTE(random_state=random_state)
            (self.splitted_vectorized_articles['X_train_resampled'], 
             self.splitted_articles['y_train_resampled']) = smote.fit_sample(self.splitted_vectorized_articles['X_train'], 
                                                                        self.splitted_articles['y_train']) 
        elif mode == 'undersample':
            rus = RandomUnderSampler('majority', random_state=random_state)
            (self.splitted_vectorized_articles['X_train_resampled'], 
             self.splitted_articles['y_train_resampled']) = rus.fit_resample(self.splitted_vectorized_articles['X_train'], 
                                                                        self.splitted_articles['y_train']) 
#        elif mode == 'oversample':
        else:
            raise Exception("mode must be 'SMOTE' or 'undersample'")


    def train_article_classifier(self, classifier='LogisticRegression', resampled=True, **params):
        """Fit classifier to training articles.
        Fit to resampled training data if resampled=True"""
        if classifier == 'LogisticRegression':
            default_params = {
                'solver' : 'saga',
                'multi_class' : 'multinomial',
                'penalty' : 'l1',
                'random_state' : 42,
                'max_iter' : 1000,
                'C' : 0.1,
                'n_jobs' : -1,
            }
        if classifier == 'DecisionTreeClassifier':
            default_params = {
                'random_state' : 42,
                'max_depth' : 2,
                'criterion' : 'gini',
                'splitter' : 'best',
                'min_samples_split' : 2,
                'min_samples_leaf' : 1,
                'max_features': None,
                'class_weight': None,
                'ccp_alpha': 0,
            }
        if classifier == 'SVC':
            default_params = {
                'kernel': 'linear',
                'C': 1,
            }
        params = {key : params.get(key, value) for key, value in default_params.items()}  
        print(f"Training {classifier} classifier with params {params}...")
        if classifier == 'LogisticRegression':
            self._classifier = LogisticRegression(**params)
        elif classifier == 'DecisionTreeClassifier':
            self._classifier = DecisionTreeClassifier(**params)
        if resampled:
            if 'X_train_resampled' not in self.splitted_vectorized_articles:
                raise Exception('Resampled data does not exist. Run Modeler.resample_articles().')
            X_train, y_train = self.splitted_vectorized_articles['X_train_resampled'], self.splitted_articles['y_train_resampled']
        else:
            X_train, y_train = self.splitted_vectorized_articles['X_train'], self.splitted_articles['y_train']
        self.classifier.fit(X_train, y_train)
        
# may want to implement tuning
# https://optunity.readthedocs.io/en/latest/

    def display_classifier_accuracy(self, display_train=False, target_names=None):
        """Print out accuracy and density of results.
        if display_train=True, show results for training set"""
        if display_train:
            y_pred = self.classifier.predict(self.splitted_vectorized_articles['X_train'])
            y_test = self.splitted_articles['y_train']
            which = 'Train'
        else:
            y_pred = self.classifier.predict(self.splitted_vectorized_articles['X_test'])
            y_test = self.splitted_articles['y_test']
            which = 'Test'
        accuracy = accuracy_score(y_test, y_pred)
        density = np.mean(self.classifier.coef_ != 0, axis=1) * 100
        print(f'{which} accuracy: {accuracy:.4f}')
        print('%% non-zero coefficients per class:\n %s' % (density))
        print(classification_report(y_test, y_pred, target_names=target_names))
        
