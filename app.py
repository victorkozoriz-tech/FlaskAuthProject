from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ContactForm, RegisterForm, LoginForm
from flask_mail import Mail, Message as MailMessage
from flask_migrate import Migrate


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.utils import secure_filename
from flask_wtf.file import FileAllowed

import itsdangerous
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['MAIL_SERVER'] = "smtp.ukr.net"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = "viktorkozoriz@ukr.net"
app.config['MAIL_PASSWORD'] = "3iEbxpjaqwfI0t8S"
app.config['MAIL_DEFAULT_SENDER'] = "viktorkozoriz@ukr.net"

db = SQLAlchemy(app)
mail = Mail(app)
serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])

def confirm_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=expiration)
    except itsdangerous.SignatureExpired:
        # Токен прострочений
        return None
    except itsdangerous.BadSignature:
        # Токен недійсний
        return None
    return email

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------ MODELS ------------------
class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Length(min=6)])
    avatar = FileField('Upload Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

class User(UserMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = (
        db.UniqueConstraint("email", name="uq_user_email"),
    )
    def __repr__(self):
        return f"<User {self.username}>"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200), default="default.png")
 

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())



with app.app_context():
    db.create_all()



# ------------------ LOGIN MANAGER ------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin",
            confirmed=True,
            avatar="default.png"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html", active="index")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Перевірка унікальності
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', "danger")
            return redirect(url_for('register'))

        # Якщо логін = admin і пароль = admin123 → роль admin
        role = "admin" if username == "admin" and password == "admin123" else "user"

        # Створення нового користувача
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()

        # ✅ Генерація токена
        token = serializer.dumps(new_user.email, salt="email-confirm")
        confirm_url = url_for('confirm_email', token=token, _external=True)

        # ✅ Надсилання HTML‑листа
        from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ContactForm, RegisterForm, LoginForm
from flask_mail import Mail, Message as MailMessage
from flask_migrate import Migrate
from datetime import datetime, timezone 

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_wtf.file import FileAllowed

import itsdangerous
import os
import pytz

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['MAIL_SERVER'] = "smtp.ukr.net"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = "viktorkozoriz@ukr.net"
app.config['MAIL_PASSWORD'] = "3iEbxpjaqwfI0t8S"
app.config['MAIL_DEFAULT_SENDER'] = "viktorkozoriz@ukr.net"

db = SQLAlchemy(app)
mail = Mail(app)
serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])
kyiv_tz = pytz.timezone("Europe/Kyiv")

def confirm_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=expiration)
    except itsdangerous.SignatureExpired:
        # Токен прострочений
        return None
    except itsdangerous.BadSignature:
        # Токен недійсний
        return None
    return email

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------ MODELS ------------------
class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Length(min=6)])
    avatar = FileField('Upload Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

class User(UserMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = (
        db.UniqueConstraint("email", name="uq_user_email"),
    )
    def __repr__(self):
        return f"<User {self.username}>"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200), default="default.png")
 

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))



with app.app_context():
    db.create_all()



# ------------------ LOGIN MANAGER ------------------

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    # створення таблиць
    db.create_all()

    # створення адміна, якщо його немає
    existing_admin = db.session.execute(
        db.select(User).filter_by(username="admin")
    ).scalar_one_or_none()

    if not existing_admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin",
            confirmed=True,
            avatar="default.png",
            created_at=datetime.now(timezone.utc)  # якщо є поле часу
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html", active="index")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # ✅ Перевірка унікальності username
        existing_user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
        if existing_user:
            flash('Username already exists!', "danger")
            return redirect(url_for('register'))

        # ✅ Перевірка унікальності email
        existing_email = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()
        if existing_email:
            flash('Email already exists!', "danger")
            return redirect(url_for('register'))

        # ✅ Визначення ролі
        role = "admin" if username == "admin" and password == "admin123" else "user"

        # ✅ Створення нового користувача
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()

        # ✅ Генерація токена
        token = serializer.dumps(new_user.email, salt="email-confirm")
        confirm_url = url_for('confirm_email', token=token, _external=True)

        # ✅ Надсилання листа
        msg = MailMessage(
            subject="Підтвердження реєстрації",
            recipients=[new_user.email]
        )
        msg.body = f"Привіт, {new_user.username}! Перейдіть за посиланням для підтвердження: {confirm_url}"
        msg.html = f"""
        <html>
          <body>
            <h2>Привіт, {new_user.username}!</h2>
            <p>Дякуємо за реєстрацію на <strong>Victor Site</strong>.</p>
            <p>Щоб підтвердити акаунт, натисніть посилання нижче:</p>
            <p><a href="{confirm_url}">Підтвердити акаунт</a></p>
            <p>Якщо кнопка не працює, скопіюйте це посилання у браузер:<br>
            {confirm_url}</p>
          </body>
        </html>
        """
        print("Sending email to:", new_user.email)
        mail.send(msg)

        flash("Реєстрація успішна! Перевірте вашу пошту для підтвердження.", "info")
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route("/confirm/<token>")
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("Посилання прострочене або недійсне.", "danger")
        return redirect(url_for("login"))

    # сучасний пошук користувача
    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not user:
        flash("Користувача з таким email не знайдено.", "danger")
        return redirect(url_for("login"))

    if user.confirmed:
        flash("Email вже підтверджено.", "info")
    else:
        user.confirmed = True
        db.session.commit()
        flash("Email підтверджено! Тепер ви можете увійти.", "success")

    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        password = form.password.data

        # ✅ Пошук користувача по username або email (SQLAlchemy 2.0)
        user = db.session.execute(
            db.select(User).where(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials!', "danger")
            return redirect(url_for('login'))

        # ❌ Якщо email не підтверджено → повторна відправка листа
        if not user.confirmed and user.role != "admin":
            token = serializer.dumps(user.email, salt="email-confirm")
            confirm_url = url_for('confirm_email', token=token, _external=True)

            msg = MailMessage(
                subject="Підтвердження реєстрації",
                recipients=[user.email]
            )
            msg.body = f"Привіт, {user.username}! Перейдіть за посиланням для підтвердження: {confirm_url}"
            msg.html = f"""
            <html>
              <body>
                <h2>Привіт, {user.username}!</h2>
                <p>Щоб підтвердити акаунт, натисніть посилання нижче:</p>
                <p><a href="{confirm_url}">Підтвердити акаунт</a></p>
                <p>Якщо кнопка не працює, скопіюйте це посилання у браузер:<br>
                {confirm_url}</p>
              </body>
            </html>
            """
            print("Resending confirmation email to:", user.email)
            mail.send(msg)

            flash("Будь ласка, підтвердіть вашу електронну пошту. Ми повторно надіслали лист із підтвердженням.", "warning")
            return redirect(url_for('login'))

        # ✅ автоматичний логін
        login_user(user)
        flash('Вхід успішний!', "success")

        # ✅ перенаправлення залежно від ролі
        if user.role == "admin":
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('contact'))

    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з системи.")
    return redirect(url_for("index"))

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        # Беремо дані з current_user
        username = current_user.username
        email = current_user.email
        message_text = request.form["message"]

        # Створюємо новий запис у таблиці Message
        new_msg = Message(
            username=username,
            email=email,
            message=message_text
        )
        db.session.add(new_msg)
        db.session.commit()

        flash("Ваше повідомлення надіслано!", "success")
        return redirect(url_for("contact"))

    # GET-запит — показуємо форму
    return render_template("contact.html")

@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Доступ заборонено. Потрібна роль адміністратора.")
        return redirect(url_for("index"))

    page = request.args.get("page", 1, type=int)
    per_page = 10

    # сучасний синтаксис SQLAlchemy 2.0
    stmt = db.select(Message).order_by(Message.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
    messages = db.session.execute(stmt).scalars().all()

    # підрахунок загальної кількості
    total_messages = db.session.execute(db.select(db.func.count(Message.id))).scalar()
    total_pages = (total_messages + per_page - 1) // per_page

    # конвертація часу у Europe/Kyiv
    from datetime import timezone
    import pytz
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    for msg in messages:
        if msg.created_at:
            msg.created_at = msg.created_at.astimezone(kyiv_tz)

    return render_template(
        "admin.html",
        messages=messages,
        page=page,
        total_pages=total_pages,
        active="admin"
    )

@app.route("/delete/<int:msg_id>", methods=["POST"])
@login_required
def delete_message(msg_id):
    if current_user.role != "admin":
        flash("Доступ заборонено.")
        return redirect(url_for("index"))

    message = Message.query.get_or_404(msg_id)
    db.session.delete(message)
    db.session.commit()
    flash("Повідомлення видалено.")
    return redirect(url_for("admin"))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data

        if form.password.data:
            current_user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join('static/avatars', filename)
            form.avatar.data.save(filepath)
            current_user.avatar = filename

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')

@app.before_request
def enforce_domain():
    url = request.url.replace("www.victor-site.xyz", "victor-site.xyz")
    if request.host.startswith("www."):
        return redirect(url, code=301)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(debug=True)
