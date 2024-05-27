# import json
# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta, timezone
# from flask_marshmallow import Marshmallow
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager, create_access_token,get_jwt,get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager
# from flask_bcrypt import Bcrypt
# from uuid import uuid4

# # from models import db, user

# api = Flask(__name__)
# CORS(api)

# ma = Marshmallow(api)

# api.config['SECRET_KEY'] = 'osteosense-flask' #any name
# # configure the SQLite database, relative to the api instance folder
# api.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/osteosense"
# api.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db=SQLAlchemy(api)

# def get_uuid():
#     return uuid4().hex

# api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# jwt = JWTManager(api)

# SQLALCHEMY_TRACK_MODIFICATION = False
# SQLALCHEMY_ECHO = True

# bcrypt = Bcrypt(api)
# # db.init_app(api)

# # with api.app_context():
# #     db.create_all

# class Doctor(db.Model):
#     __tablename__ = "doctors"
#     id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
#     name = db.Column(db.String(150), unique=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.Text, nullable=False)
#     about = db.Column(db.Text, nullable=False)

# class Users(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100))
#     date = db.Column(db.DateTime, default=datetime.now)

#     def __init__(self, name, email):
#         self.name = name
#         self.email = email

# class UserSchema(ma.Schema):
#     class Meta:
#         # Fields to expose
#         fields = ("id", "name", "email", "date")

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# @api.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# @api.route('/listusers',methods = ['GET'])
# def listusers():
#     all_users = Users.query.all()
#     results = users_schema.dump(all_users)
#     return jsonify(results)

# @api.route('/userdetails/<id>',methods = ['GET'])
# def userdetails(id):
#     user = Users.query.get(id)
#     return user_schema.jsonify(user)

# @api.route('/userupdate/<id>',methods = ['PUT'])
# def userupdate(id):
#     user = Users.query.get(id)

#     name = request.json['name']
#     email = request.json['email']

#     user.name = name
#     user.email = email

#     db.session.commit()
#     return user_schema.jsonify(user)

# @api.route('/userdelete/<id>',methods = ['DELETE'])
# def userdelete(id):
#     user = Users.query.get(id)
#     db.session.delete(user)
#     db.session.commit()
#     return user_schema.jsonify(user)


# @api.route("/useradd", methods=['POST'])
# def useradd():
#     try:
#         name = request.json['name']
#         email = request.json['email']

#         user = Users(name, email)
#         db.session.add(user)
#         db.session.commit()
#         return user_schema.jsonify(user)

#         # return jsonify({"success": "User added successfully"})
#     except Exception as e:
#         # Rollback the session in case of an error
#         db.session.rollback()
#         # Return the error message
#         return jsonify({"error": str(e)}), 500

# @api.route('/logintoken', methods=["POST"])
# def create_token():

#     email = request.json.get('email', None)
#     password = request.json.get('password', None)

#     doctor = Doctor.query.filter_by(email=email).first()

#     # if email != "test" or password != "test":
#     #     return {"msg": "Wrong email or password"}, 401

#     if doctor is None:
#         return jsonify({"error": "Wrong email or password"}), 401

#     if not bcrypt.check_password_hash(doctor.password, password):
#         return jsonify ({"error": "Unauthorized"}), 401

#     access_token = create_access_token(identity=email)
#     # response =  {"access_token": access_token}

#     return jsonify({
#         "email": email,
#         "access_token": access_token
#     })
#     # return response

# @api.route("/signup", methods=["POST"])
# def signup():
#     email = request.json["email"]
#     password = request.json["password"]

#     user_exists = Doctor.query.filter_by(email=email).first() is not None

#     if user_exists:
#         return jsonify({"error": "Email already exists"}), 409

#     hashed_password = bcrypt.generate_password_hash(password)
#     new_user = Doctor(name="doctor3", email=email, password=hashed_password, about="sample about doctor3")
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({
#         "message": "User successfully signed up",
#         "email": email
#     }), 201

# @api.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             data = response.get_json()
#             if type(data) is dict:
#                 data["access_token"] =  access_token
#                 response.data = json.dumps(data)
#         return response

#     except (RuntimeError, KeyError):
#         # Case where there is not a valid JWT. Just return the original response
#         return response

# @api.route("/logout", methods=["POST"])
# def logout():
#     response = jsonify({"msg": "logout successful"})
#     unset_jwt_cookies(response)
#     return response

# @api.route('/profile/<getemail>')
# @jwt_required()
# def my_profile(getemail):
#     print(getemail)
#     if not getemail:
#         return jsonify({"error": "Unauthorized Access"}), 401

#     doctor = Doctor.query.filter_by(email=getemail).first()

#     response_body = {
#         "id": doctor.id,
#         "name": doctor.name,
#         "email": doctor.email,
#         "about": doctor.about,
#     }

#     return response_body


# TESTING SEPERATE

import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    unset_jwt_cookies,
    jwt_required,
)

api = Flask(__name__)
CORS(api)

ma = Marshmallow(api)

api.config["SECRET_KEY"] = "osteosense-flask"
api.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/osteosense"
api.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(api)

bcrypt = Bcrypt(api)

api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(api)


@api.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response

    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


# Import the routes from routes.py
import routes

if __name__ == "__main__":
    api.run()
