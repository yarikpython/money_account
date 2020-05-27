from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from new_mon_acc.models import User


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_conf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Sorry, this email address has already taken')


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddCatForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')


class AddNoteForm(FlaskForm):
    spend = StringField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_spend(self, spend):
        if ',' in spend.data:
            raise ValidationError('Please use "." instead of ","')
        elif not spend.data.replace('.', '').isdigit():
            raise ValidationError('Incorrect data')


class CreateReportForm(FlaskForm):
    start = DateTimeField('From', validators=[DataRequired()])
    finish = DateTimeField('To', validators=[DataRequired()])
    submit = SubmitField('Create Report')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password_conf = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Accept New Password')