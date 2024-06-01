from enum import unique
from operator import index
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
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    phoneno = db.Column(db.String(15), unique=True, nullable=False)


# ADMIN
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


# PATIENT
class Patient(db.Model):
    # Table name for the Doctor model
    __tablename__ = "patients"

    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    fullname = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(3), nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phoneno = db.Column(db.String(15), unique=True, nullable=False)


# PREDICTION
class Prediction(db.Model):
    __tablename__ = "imageprediction"

    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    fullname = db.Column(db.String(150), nullable=False)
    age = db.Column(db.String(3), nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    datetimeprediction = db.Column(db.DateTime, nullable=False, default=datetime.now)
    resultprediction = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phoneno = db.Column(db.String(15), nullable=False)
    doctorid = db.Column(db.String(11), nullable=False)
    imageprediction = db.Column(db.String(120), index=True, nullable=False)


# IMAGE UPLOAD TEST
class Images(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True, unique=True)
