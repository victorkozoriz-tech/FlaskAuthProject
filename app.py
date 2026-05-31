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
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)
serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])
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
            flash('Username already exists!')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists!')
            return redirect(url_for('register'))

        # Якщо логін = admin і пароль = admin123 → роль admin
        if username == "admin" and password == "admin123":
            role = "admin"
        else:
            role = "user"

        # Створення нового користувача
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            confirmed=True   # тимчасово без перевірки email
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)  # 1 година
    except itsdangerous.SignatureExpired:
        flash("Посилання прострочене.", "danger")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first_or_404()
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
        username_or_email = form.username.data
        password = form.password.data

        # Пошук користувача по username або email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials!')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully!')

        # Перенаправлення залежно від ролі
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
    paginations = Message.query.order_by(Message.created_at.desc()).paginate(page=page, per_page=10)

    return render_template(
        "admin.html",
        messages=paginations.items,
        page=page,
        total_pages = paginations.pages if paginations.pages > 0 else 1,
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

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(debug=True)
