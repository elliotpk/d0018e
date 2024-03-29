from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    FileField,
)
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Optional, Email, Length, EqualTo, NumberRange

class login_form(FlaskForm):
    email = StringField(validators=[Optional(), Email()])
    pwd = PasswordField(validators=[InputRequired(), Length(8,72)])

class register_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(8, 72)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(validators=[InputRequired(), Length(8,72), EqualTo("pwd", message="Passwords must match")])

class addItem_form(FlaskForm):

    name = StringField(validators=[InputRequired(),Length(0,72)] )
    image = FileField(validators=[Optional()])
    price = IntegerField(validators=[Optional()])
    description = StringField(validators=[Optional(),Length(0,255)])

class addAttribute_form(FlaskForm):
    attributename = StringField(validators=[InputRequired(),Length(0,72)] )

class addAttributeValue_form(FlaskForm):
    attributevalue = StringField(validators=[InputRequired(), Length(0, 72)],)

class cardCredential_form(FlaskForm):
    banknr=StringField(validators=[InputRequired(), Length(0, 72)])
    expdate=StringField(validators=[InputRequired()])
    cvs=StringField(validators=[InputRequired(), Length(3,3)])

class comment_form(FlaskForm):
    text = StringField(validators=[Optional(), Length(0,300)])
    rating = IntegerField(validators=[InputRequired(), NumberRange(0,10)])
