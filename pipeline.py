import pandas as pd
import configparser
import json
from topic_modeler.modeling import Modeler


cfg = ConfigParser()
cfg.read('topic_modeler/settings.ini')


# scrape earther
# NOTE THAT IF YOU RESCRAPE EARTHER THE TOPIC CLUSTERS WILL CHANGE!!

modeler = Modeler()

cluster_cfg = cfg['CLUSTERING']
pd.set_option('display.max_columns', cluster_cfg['N_CLUSTERS'])

modeler.vectorize_keywords(**json.loads(cluster_cfg['KEYWORD_VECTORIZER_SETTINGS']))

modeler.silhouette_analysis(start=json.loads(cluster_cfg['N_CLUSTERS']) - 2,
                            end=json.loads(cluster_cfg['N_CLUSTERS']) + 2,
                            vectorization=json.loads(cluster_cfg['KEYWORD_VECTORIZER_SETTINGS'])['vectorizer'],
                            random_state=json.loads(cluster_cfg['RANDOM_STATE'])
                            
modeler.cluster_keywords(json.loads(cluster_cfg['N_CLUSTERS']),
                         random_state=json.loads(cluster_cfg['RANDOM_STATE']))

modeler.display_keyword_clusters()

modeler.save_clusters_to_mongodb()

modeler.test_train_split()

modeler.vectorize_articles()

modeler.resample_articles()

# in theory could do this on AWS/GoogleCloud to go faster:

modeler.train_article_classifier()


# scrape new content

# classify and display somehow

# app - put in url or text, classify

# display from news rss feed classify most recent stories ?????