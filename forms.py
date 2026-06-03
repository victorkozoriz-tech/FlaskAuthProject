from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

# ------------------ Register Form ------------------
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

# ------------------ Login Form ------------------
class LoginForm(FlaskForm):
    # універсальне поле: можна вводити і username, і email
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# ------------------ Contact Form ------------------
class ContactForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Send')
