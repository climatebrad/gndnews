import datetime
import pandas as pd
import configparser
import json
from topic_modeler.modeling import Modeler


cfg = ConfigParser()
cfg.read('topic_modeler/settings.ini')
random_state=json.loads(cfg['DEFAULT']['RANDOM_STATE'])

# scrape earther
# NOTE THAT IF YOU RESCRAPE EARTHER THE TOPIC CLUSTERS WILL CHANGE!!

modeler = Modeler()

"""Do Topic Clustering"""

cluster_cfg = cfg['CLUSTERING']

pd.set_option('display.max_columns', cluster_cfg['N_CLUSTERS'])

modeler.vectorize_keywords(**json.loads(cluster_cfg['KEYWORD_VECTORIZER_SETTINGS']))

# optional to try to find best random state
# modeler.try_random_random_states()

modeler.silhouette_analysis(start=json.loads(cluster_cfg['N_CLUSTERS']) - 2,
                            end=json.loads(cluster_cfg['N_CLUSTERS']) + 2,
                            random_state=random_state)
                            
modeler.cluster_keywords(json.loads(cluster_cfg['N_CLUSTERS']),
                         random_state=random_state)

modeler.display_keyword_clusters()

modeler.save_clusters_to_mongodb()
                            
"""Do Article Text Modeling"""

# in theory could do this on AWS/GoogleCloud to go faster

model_cfg = cfg['TOPIC_MODELING']
                            
modeler.train_test_split_articles(random_state=random_state)

modeler.vectorize_articles(**json.loads(model_cfg['ARTICLE_VECTORIZER_SETTINGS']))

modeler.resample_articles(**json.loads(model_cfg['ARTICLE_VECTORIZER_SETTINGS']), 
                          random_state=random_state)



modeler.train_article_classifier(classifier=model_cfg['MODEL'], 
                                 **json.loads(model_cfg['MODEL_SETTINGS']),
                                 random_state=random_state
                                )

modeler.display_classifier_accuracy()
                                  
modeler.save_classifier_to_file("classifier" + str(int(datetime.datetime.now().timestamp())))                                
                                  
# scrape new content

# classify and display somehow

# app - put in url or text, classify

# display from news rss feed classify most recent stories ?????
