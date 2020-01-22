from flask import render_template
from app import app
from app.forms import TextForm


@app.route('/')
@app.route('/index')
def index():
    topics = ["Cars","Drought","Endangered Species","Extreme Weather","Flint Water Crisis","Interior Department","Antarctica","Arctic","Volcanoes","Air Pollution","Pipeline Activism","Amazon Rainforest","EPA","Meteorology","General Climate","Plastic Pollution","ANWR","FEMA","Green New Deal","California Wildfires","Renewable Energy","Recycling","Trump Administration","Puerto Rico Hurricanes","Youth Climate Activism","Conservation","Indigenous Rights","2020 Election","General News","Australia Wildfires"]
    form = TextForm()
    return render_template('index.html', topics=topics, form=form)

