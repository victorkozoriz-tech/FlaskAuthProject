from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class ContactForm(FlaskForm):
    name = StringField("Ім’я", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    content = TextAreaField("Повідомлення", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Відправити")

class RegisterForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Підтвердження пароля", validators=[
        DataRequired(),
        EqualTo("password", message="Паролі повинні співпадати")
    ])
    submit = SubmitField("Зареєструватися")

class LoginForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Увійти")    