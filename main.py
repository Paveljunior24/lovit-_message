from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'  # Chemin de la base de données SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Définition du modèle de la base de données
class User (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=True, unique = True)
    password = db.Column(db.String(50), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)


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


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/register")
def register():
    return render_template('register.html')
# Point d'entrée principal de l'application Flask
if __name__ == "__main__":
    with app.app_context():
        # Création de toutes les tables de la base de données si elles n'existent pas encore
        db.create_all()
        
        # Lancement de l'application en mode débogage
        app.run(debug=True)
