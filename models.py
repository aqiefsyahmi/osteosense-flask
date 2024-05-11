from app import db
from datetime import datetime
from uuid import uuid4

def get_uuid():
    return uuid4().hex


# DOCTORS
class Doctor(db.Model):
    # Table name for the Doctor model
    __tablename__ = "doctors"

    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)

    # DOCTORS
class Admin(db.Model):
    # Table name for the Doctor model
    __tablename__ = "admin"

    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), nullable=False)

class Users(db.Model):
    # Table name for the Users model
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, email):
        # Constructor method for the Users model
        self.name = name
        self.email = email