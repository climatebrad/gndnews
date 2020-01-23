"""
author: @climatebrad
"""

import json
import joblib
from sklearn.pipeline import Pipeline

class NewsifierMixin():
    
    @property
    def cluster_names(self):
        """names of cluster numbers from configs"""
        if self._cluster_names is None:
            self._cluster_names = json.loads(self.cfg['CLUSTERING']['CLUSTER_NAMES'])
        return self._cluster_names
    
    @property
    def text_classifier(self):
        """text_classifier pipeline"""
        if self._text_classifier is None:
            self._text_classifier = Pipeline([
                ('tfidf', modeler.article_vectorizer),
                ('clf', modeler.classifier),
            ])
        return self._text_classifier

    def save_classifier_to_file(self, filename):
        """save to a joblib file (do not include extension in filename)"""
        text_clf = Pipeline([
            ('tfidf', self.article_vectorizer),
            ('clf', self.classifier),
        ])
        joblib.dump(text_clf, filename + ".joblib.gz", compress=('gzip', 3))
        
    def load_classifier(self, filename, extension='.joblib.gz'):
        """load from a joblib file (filname does not include extension)"""
        text_clf = joblib.load(filename + extension)
        self._text_classifier = text_clf
        self._article_vectorizer = text_clf[0]
        self._classifier = text_clf[1]
        
    def sorted_cluster_predictions(self, text : str):
        """given text string, return list of topics sorted by probability"""
        return [
                 { 'topic' : k,  'prob' : v } for k, v in sorted(
                    { self.cluster_names[i] : x 
                                    for i, x in enumerate(
                                        self.text_classifier.predict_proba(
                                            [text]
                                        )[0]
                                    ) 
                    }.items(),
                    key=lambda item: item[1],
                    reverse=True)
        ]

    def top_topics(self, idx_or_text, num=3):
        """print the highest-probability topics for a given article index or text string"""
        if isinstance(idx_or_text, int):
            print(self.articles.iloc[idx_or_text].title)
            text = self.articles.iloc[idx_or_text].body_text
        else:
            text = idx_or_text
        return self.sorted_cluster_predictions(text)[:num]
        
    def predict_url(self, url):
        """take url and display predictions."""
        # TODO: error checking on URL
        print(url)
        text = self._text_from_html(requests.get(url).content)
        return self.display_formatted_predictions(text)
    
    @staticmethod
    def _text_from_html(body):
        """helper method to get visible text from html"""
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        return u" ".join(t.strip() for t in texts)


    def display_formatted_predictions(self, text):
        """Do one's best with explaining model output"""
        ignore = () # ('Biology and Climate')
        general = ('General Climate')
        predictions = self.sorted_cluster_predictions(text)
        result = ''
        top = predictions.pop(0)
        while top['topic'] in ignore:
            top = predictions.pop(0)
        if (top['topic'] in general and top['prob'] < .32) or (top['prob'] < .1):
            result += "This is probably not about climate.\n"
            result += f"(The best-scoring topic is {top['topic']} at {top['prob']:.2%})\n"
            return result
        if top['prob'] > .9:
                result += f"This is almost definitely about {top['topic']} ({top['prob']:.2%}).\n"
        else:
            result += f"The best-scoring topic is {top['topic']} at {top['prob']:.2%}\n"
        top = predictions.pop(0)
        while top['prob'] > .05:
            if top['topic'] not in ignore:
                result += f"* {top['topic']} ({top['prob']:.2%})"
            top = predictions.pop(0) 
        return result
