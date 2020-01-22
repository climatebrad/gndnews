import re
from topic_modeler.modeler import Modeler

class GizmodoModeler(Modeler):
    """model on Gizmodo"""
    
    
    def __init__(self):
        super().__init__('gizmodo.ini')
        self.articles['cluster'] = self.articles.url.map(self.extract_site)
        
    @staticmethod
    def extract_site(url):
        return re.search('((?:earther\.|io9\.)?\w+\.com)/?', url).group(1)
    
    def drop_gizmodo_site(self, sitename):
        """Drop articles with sitename in cluster column"""
        self._articles = self.articles[self.articles.cluster != sitename]
    
    
    
    
    