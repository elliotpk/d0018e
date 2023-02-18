from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
)
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Optional

class login_form(FlaskForm):
    username = StringField(validators=[Optional()])
    pwd = PasswordField(validators=[InputRequired()])