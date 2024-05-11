from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import urandom

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

# Initialize SQLAlchemy for database management
db = SQLAlchemy()

def create_app():
    # Initialize Flask app instance
    app = Flask(__name__)
    
    # Generate a secret key
    app.secret_key = urandom(24)
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///healthx.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Bcrypt and SQLAlchemy with the app
    bcrypt.init_app(app)
    db.init_app(app)

    # Register blueprints
    from .routes import bp
    app.register_blueprint(bp)

    return app


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    reports = db.relationship('Report', backref='patient', lazy=True)

    def __repr__(self):
        return f"Patient('{self.username}', '{self.email}')"

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    reports = db.relationship('Report', backref='doctor', lazy=True)

    def __repr__(self):
        return f"Doctor('{self.username}', '{self.email}')"

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptoms = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    is_appointment = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Report('{self.date_uploaded}', '{self.patient_id}', '{self.doctor_id}', '{self.is_appointment}')"
