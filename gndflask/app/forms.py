from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class TextForm(FlaskForm):
    text = TextAreaField('Input Text', render_kw={'class': 'form-control', 'rows': 20})
    submitbutton = SubmitField('Submit')