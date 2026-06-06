from flask import Flask
from flask_mail import Mail, Message as MailMessage

app = Flask(__name__)

app.config['MAIL_SERVER'] = "smtp.ukr.net"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = "viktorkozoriz@ukr.net"
app.config['MAIL_PASSWORD'] = "3iEbxpjaqwfI0t8S"
app.config['MAIL_DEFAULT_SENDER'] = "viktorkozoriz@ukr.net"

mail = Mail(app)

# ✅ Використовуємо контекст додатка
with app.app_context():
    msg = MailMessage(
        subject="Тест",
        recipients=["viktorkozoriz@ukr.net"],
        body="Це тестовий лист від Flask."
    )
    mail.send(msg)
    print("Лист відправлено!")
