#
# 
#
#


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


# A class for user registration using WTForms.
class RegistrationForm(FlaskForm):

    username = StringField('Username', validators = [DataRequired(), Length(min = 1, max = 20)])

    first_name = StringField('First Name', validators = [DataRequired(), Length(min = 1)])
    last_name = StringField('Last Name', validators = [DataRequired(), Length(min = 1)])

    email = StringField('Email', validators = [DataRequired(), Email()])

    password = PasswordField('Password', validators = [DataRequired(), Length(min = 6)])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), Length(min = 6), EqualTo('password')])

    submit = SubmitField('Sign Up')


# A class for user login using WTForms.
class LoginForm(FlaskForm):

    username = StringField('Username', validators = [DataRequired(), Length(min = 1, max = 20)])

    password = PasswordField('Password', validators = [DataRequired(), Length(min = 6)])

    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Log In')