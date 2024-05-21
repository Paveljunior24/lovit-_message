from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'  # Chemin de la base de données SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisakey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view ="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Définition du modèle de la base de données
class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=True, unique = True)
    password = db.Column(db.String(50), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "password"})

    submit = SubmitField("Register")

    def valdate_username(self, username):
        existing_user_name = User.query.filter_by(
            username=username.data).first()

        if existing_user_name:
            raise ValidationError(
                "This Username already exists , please choose a difeerent one.") 

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "password"})

    submit = SubmitField("login")

        

# Route principale de l'application
@app.route("/")
def welcome():
    return render_template('welcome.html')


@app.route("/get-messages/<name>", methods=['GET', 'POST'])
def get_messages(name):
    if request.method == 'POST':
        # Si une requête POST est reçue, enregistrer un nouveau message dans la base de données
        new_message = Message(
            user=name,
            content=request.form['content']
        )
        db.session.add(new_message)
        db.session.commit()

    # Récupération de tous les messages de la base de données et les trier par date de création
    messages = Message.query.order_by(Message.created_at).all()
    
    # Rendu de la page HTML avec les messages récupérés et le nom passé en paramètre
    return render_template('messages.html', messages=messages, name=name)


@app.route("/login", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html', form=form)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route("/logout", methods= ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Check if the username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # If the username doesn't exist, proceed with registration
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred while registering. Please try again later.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)




# Point d'entrée principal de l'application Flask
if __name__ == "__main__":
    with app.app_context():
        # Création de toutes les tables de la base de données si elles n'existent pas encore
        db.create_all()
        
        # Lancement de l'application en mode débogage
        app.run(debug=True)
