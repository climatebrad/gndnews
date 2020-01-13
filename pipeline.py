import configparser

from topic_modeler.modeling import Modeler

cfg = ConfigParser()
cfg.read('topic_modeler/settings.py')

modeler = Modeler()

modeler.vectorize_keywords(vectorizer=cfg['KEYWORD_VECTORIZER_SETTINGS']['vectorizer'],
                           gizmodo=cfg['KEYWORD_VECTORIZER_SETTINGS']['gizmodo'])

modeler.cluster_keywords(cfg['N_CLUSTERS'], random_state=cfg['RANDOM_STATE'])

modeler.display_keyword_clusters()

modeler.save_clusters_to_mongodb()


