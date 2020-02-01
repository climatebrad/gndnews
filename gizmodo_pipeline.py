import datetime
import pandas as pd
import configparser
import json
from topic_modeler.modeling import Modeler

# scrape gizmodo

gizmodeler = Modeler()
gizmodeler.drop_gizmodo_site('io9.gizmodo.com')
cfg = gizmodeler.cfg
random_state=cfg['DEFAULT'].getint(['RANDOM_STATE'])

# We probably want to remove crossposted articles from the train/test. 
# Would be good to have them so we can see if classifier puts them in both/multiple categories.
# unfortunately only way to do that would be to track the outgoing links of the index pages, which we didn't do.
                            
"""Do Article Text Modeling"""

# in theory could do this on AWS/GoogleCloud to go faster

model_cfg = cfg['TOPIC_MODELING']
                            
gizmodeler.train_test_split_articles(random_state=random_state)

gizmodeler.vectorize_articles(**json.loads(model_cfg['ARTICLE_VECTORIZER_SETTINGS']))



gizmodeler.train_article_classifier(classifier=model_cfg['MODEL'], 
                                 **json.loads(model_cfg['MODEL_SETTINGS']),
                                 random_state=random_state
                                )

gizmodeler.display_classifier_accuracy()
                                  
gizmodeler.save_classifier_to_file("gizmodo_classifier" + str(int(datetime.datetime.now().timestamp())))                                
                                  
# scrape new content

# classify and display somehow

# app - put in url or text, classify

# display from news rss feed classify most recent stories ?????
