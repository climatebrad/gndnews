from flask import render_template
from app import app
from app.forms import TextForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    topics = ["Cars","Drought","Endangered Species","Extreme Weather","Flint Water Crisis","Interior Department","Antarctica","Arctic","Volcanoes","Air Pollution","Pipeline Activism","Amazon Rainforest","EPA","Meteorology","General Climate","Plastic Pollution","ANWR","FEMA","Green New Deal","California Wildfires","Renewable Energy","Recycling","Trump Administration","Puerto Rico Hurricanes","Youth Climate Activism","Conservation","Indigenous Rights","2020 Election","General News","Australia Wildfires"]
    form = TextForm()
    if form.validate_on_submit():
        results = get_results(form.text.data)
        return render_template('results.html', text=form.text.data, results=results, title='categorizer')
    return render_template('index.html', topics=topics, form=form)

def get_results(text):
    results = app.classifier.top_topics(text)
    return results

@app.route('/topics/<topic>')
def display_topic(topic):
    return render_template('topic.html', topic=topic, title=topic)

