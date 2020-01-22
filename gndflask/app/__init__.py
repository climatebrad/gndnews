from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from topic_modeler.modeler import Modeler

app = Flask(__name__)
app.config.from_object(Config)
from app import routes

modeler = Modeler()
modeler.load_classifier('classifier2_0.59')

bootstrap = Bootstrap(app)

