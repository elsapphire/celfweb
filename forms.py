from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, DateField, IntegerField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(Email)])
    password = PasswordField('Choose A Password', validators=[DataRequired()])
    password_confirmation = PasswordField('Password Again', validators=[DataRequired()])
    submit = SubmitField('SIGN ME UP!')


class AutomateForm(FlaskForm):
    name_of_week = StringField('Type of Meeting', validators=[DataRequired()])
    date_of_meeting = DateField('Date Meeting Held', validators=[DataRequired()])
    attendance = IntegerField('Range for Attendance', validators=[DataRequired()])

