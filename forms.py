from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
)
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Optional, Email, Length, EqualTo

class login_form(FlaskForm):
    email = StringField(validators=[Optional(), Email()])
    pwd = PasswordField(validators=[InputRequired(), Length(8,72)])

class register_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(8, 72)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(validators=[InputRequired(), Length(8,72), EqualTo("pwd", message="Passwords must match")])