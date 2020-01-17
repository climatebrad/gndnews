"""
author: @climatebrad
"""

import json
from sklearn.pipeline import Pipeline

class NewsifierMixin():
    
    @property
    def cluster_names(self):
        if self._cluster_names is None:
            self._cluster_names = json.loads(self.cfg['CLUSTERING']['CLUSTER_NAMES'])
        return self._cluster_names
    
    @property
    def text_classifier(self):
        if self._text_classifier is None:
            self._text_classifier = Pipeline([
                ('tfidf', modeler.article_vectorizer),
                ('clf', modeler.classifier),
            ])
        return self._text_classifier
    
    def top_cluster_predictions(self, vectorized_text, num=2):
        sorted_probs = {
            k : v for k, v in sorted(
                { self.cluster_names[i] : x 
                                for i, x in enumerate(
                                    self.classifier.predict_proba(
                                        text
                                    )[0]
                                ) 
                }.items(),
                key=lambda item: item[1],
                reverse=True)
        }
        return list(sorted_probs)[:num]

    def top_topics(self, idx_or_text, num=3):
        if isinstance(idx_or_text, int):
            print(self.articles.iloc[idx_or_text].title)
            vectorized_text = self.vectorized_articles[idx_or_text]
        else:
            vectorized_text = self.article_vectorizer.transform(text)
        print(self.top_cluster_predictions(vectorized_text, num))
