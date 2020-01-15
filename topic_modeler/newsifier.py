"""
author: @climatebrad
"""

class NewsifierMixin():
    
    @property
    def cluster_names(self):
        if self._cluster_names is None:
            self._cluster_names = json.loads(self.cfg['CLUSTERING']['CLUSTER_NAMES'])
        return self._cluster_names
    
    def top_cluster_predictions(self, idx, num=2):
    sorted_probs = {
        k : v for k, v in sorted(
            { self.cluster_names[i] : x 
                            for i, x in enumerate(
                                self.classifier.predict_proba(
                                    self.vectorized_articles[idx]
                                )[0]
                            ) 
            }.items(),
            key=lambda item: item[1],
            reverse=True)
    }
    return list(sorted_probs)[:num]

    def top_topics(self, idx, num=3):
        print(self.articles.iloc[idx].title)
        print(self.top_cluster_predictions(idx, num))