"""
author: @climatebrad
"""
from configparser import ConfigParser
from topic_modeler.newsifier import NewsifierMixin

class Classifier(NewsifierMixin):
    """stripped down class to implement modeling with trained model"""
    def __init__(self, settings_file='settings.ini'):
        self._settings_file = settings_file
        self._cfg = None
        self._cluster_names = None
        self._article_vectorizer = None
        self._classifier = None
        self._text_classifier = None
        
    @property 
    def cfg(self):
        if self._cfg is None:
            cfg = ConfigParser()
            cfg.read(self._settings_file)
            self._cfg = cfg
        return self._cfg
    
    @property
    def article_vectorizer(self):
        """vectorizer"""
        if self._article_vectorizer is None:
            raise Exception("Vectorizer is not defined. Load trained model.")
        return self._article_vectorizer
    
    @property
    def classifier(self):
        """classifier model"""
        if self._classifier is None:
            raise Exception("Classifer is not defined. Load trained model.")
        return self._classifier
