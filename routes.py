from io import BytesIO
from unittest import result
from PIL import Image
import cv2
import numpy as np
from sqlalchemy import false
import tensorflow as tf

# for image
import os
import urllib.request
from werkzeug.utils import secure_filename

from app import api, db, bcrypt
from models import Doctor, Users, Admin, Patient, Prediction, Images
from schemas import (
    UserSchema,
    AdminSchema,
    DoctorSchema,
    PatientSchema,
    PredictionSchema,
    ImageSchema,
)
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)

doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)

patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)

prediction_schema = PredictionSchema()
predictions_schema = PredictionSchema(many=True)

image_schema = ImageSchema()
images_schema = ImageSchema(many=True)


@api.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# USERS


@api.route("/listusers", methods=["GET"])
def listusers():
    all_users = Users.query.all()
    results = users_schema.dump(all_users)
    return jsonify(results)


@api.route("/userdetails/<id>", methods=["GET"])
def userdetails(id):
    user = Users.query.get(id)
    return user_schema.jsonify(user)


@api.route("/userupdate/<id>", methods=["PUT"])
def userupdate(id):
    user = Users.query.get(id)

    name = request.json["name"]
    email = request.json["email"]

    user.name = name
    user.email = email

    db.session.commit()
    return user_schema.jsonify(user)


@api.route("/userdelete/<id>", methods=["DELETE"])
def userdelete(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


@api.route("/useradd", methods=["POST"])
def useradd():
    try:
        name = request.json["name"]
        email = request.json["email"]

        user = Users(name, email)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)

        # return jsonify({"success": "User added successfully"})
    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


# DOCTORS


@api.route("/logintokendoctors", methods=["POST"])
def create_token():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    print("Received data:", email, password)

    doctor = Doctor.query.filter_by(email=email).first()

    if doctor and bcrypt.check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=doctor.id)
        return jsonify(
            {
                "message": "Login Success",
                "doctor_token": access_token,
                "email": email,
                "id": doctor.id,
            }
        )
    else:
        return jsonify({"message": "Login Failed"}), 401


@api.route("/signupdoctor", methods=["POST"])
def signupdoctor():
    try:
        # Extracting fields from the JSON request
        email = request.json.get("email")
        username = request.json.get("username")
        password = request.json.get("password")
        fullname = request.json.get("fullname")
        phoneno = request.json.get("phoneno")

        # Check if the email already exists
        user_exists = Doctor.query.filter_by(email=email).first() is not None

        if user_exists:
            return jsonify({"error": "Email already exists"}), 409

        # Hashing the password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Creating a new doctor user
        new_user = Doctor(
            username=username,
            email=email,
            password=hashed_password,
            fullname=fullname,
            phoneno=phoneno,
        )

        # Adding and committing the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User successfully signed up", "email": email}), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


@api.route("/listdoctors", methods=["GET"])
def listdoctors():
    all_doctors = Doctor.query.all()
    results = doctors_schema.dump(all_doctors)
    return jsonify(results)


@api.route("/doctordetails/<id>", methods=["GET"])
def doctordetails(id):
    doctor = Doctor.query.get(id)
    return doctor_schema.jsonify(doctor)


@api.route("/doctorupdate/<id>", methods=["PUT"])
def doctorupdate(id):
    doctor = Doctor.query.get(id)

    fullname = request.json["fullname"]
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    phoneno = request.json["phoneno"]

    if fullname:
        doctor.fullname = fullname
    if username:
        doctor.username = username
    if email:
        doctor.email = email
    if password:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        doctor.password = hashed_password
    if phoneno:
        doctor.phoneno = phoneno

    db.session.commit()
    return doctor_schema.jsonify(doctor)


@api.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@api.route("/profile/<getemail>")
def my_profile(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401

    doctor = Doctor.query.filter_by(email=getemail).first()

    response_body = {
        "id": doctor.id,
        "fullname": doctor.fullname,
        "username": doctor.username,
        "email": doctor.email,
        "phoneno": doctor.phoneno,
    }

    return response_body


@api.route("/doctordelete/<id>", methods=["DELETE"])
def doctordelete(id):
    doctor = Doctor.query.get(id)
    db.session.delete(doctor)
    db.session.commit()
    return doctor_schema.jsonify(doctor)


# ADMIN


@api.route("/logintokenadmin", methods=["POST"])
def create_token_admin():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    print("Received data:", email, password)

    admin = Admin.query.filter_by(email=email).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        access_token = create_access_token(identity=admin.id)
        return jsonify(
            {
                "message": "Login Success",
                "admin_token": access_token,
                "email": email,
                "id": admin.id,
            }
        )
    else:
        return jsonify({"message": "Login Failed"}), 401


@api.route("/signupadmin", methods=["POST"])
def signupadmin():
    email = request.json["email"]
    password = request.json["password"]

    user_exists = Admin.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = Admin(username="admin", email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User successfully signed up", "email": email}), 201


@api.route("/admindetails/<id>", methods=["GET"])
def admindetails(id):
    admin = Admin.query.get(id)
    return admin_schema.jsonify(admin)


@api.route("/adminupdate/<id>", methods=["PUT"])
def adminupdate(id):
    admin = Admin.query.get(id)

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if username:
        admin.username = username
    if email:
        admin.email = email
    if password:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        admin.password = hashed_password

    db.session.commit()
    return admin_schema.jsonify(admin)


@api.route("/logoutadmin", methods=["POST"])
def logoutadmin():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@api.route("/profileadmin/<getemail>")
def my_profile_admin(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401

    admin = Admin.query.filter_by(email=getemail).first()

    response_body = {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
    }

    return response_body


# PATIENT


@api.route("/signuppatient", methods=["POST"])
def signuppatient():
    try:
        # Extracting fields from the JSON request
        fullname = request.json.get("fullname")
        age = request.json.get("age")
        gender = request.json.get("gender")
        email = request.json.get("email")
        phoneno = request.json.get("phoneno")

        # Check if the email already exists
        user_exists = Patient.query.filter_by(email=email).first() is not None

        if user_exists:
            return jsonify({"error": "Email already exists"}), 409

        # Creating a new patient
        new_user = Patient(
            fullname=fullname, age=age, gender=gender, email=email, phoneno=phoneno
        )

        # Adding and committing the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify(
            {
                "message": "User successfully signed up",
                "fullname": fullname,
                "email": email,
                "age": age,
                "gender": gender,
                "phoneno": phoneno,
            }
        ), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


@api.route("/listpatients", methods=["GET"])
def listpatients():
    all_patients = Patient.query.all()
    results = patients_schema.dump(all_patients)
    return jsonify(results)


@api.route("/patientdetails/<id>", methods=["GET"])
def patientdetails(id):
    patient = Patient.query.get(id)
    return patient_schema.jsonify(patient)


@api.route("/patientupdate/<id>", methods=["PUT"])
def patientupdate(id):
    patient = Patient.query.get(id)

    fullname = request.json["fullname"]
    age = request.json["age"]
    gender = request.json["gender"]
    email = request.json["email"]
    phoneno = request.json["phoneno"]

    if fullname:
        patient.fullname = fullname
    if age:
        patient.age = age
    if gender:
        patient.gender = gender
    if email:
        patient.email = email
    if phoneno:
        patient.phoneno = phoneno

    db.session.commit()
    return patient_schema.jsonify(patient)


@api.route("/patientprofile/<getemail>")
def patientprofile(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401

    patient = Patient.query.filter_by(email=getemail).first()

    response_body = {
        "id": patient.id,
        "fullname": patient.fullname,
        "username": patient.username,
        "email": patient.email,
        "phoneno": patient.phoneno,
    }

    return response_body


@api.route("/patientdelete/<id>", methods=["DELETE"])
def patientdelete(id):
    patient = Patient.query.get(id)
    db.session.delete(patient)
    db.session.commit()
    return patient_schema.jsonify(patient)


# PREDICTION DATA


@api.route("/addprediction", methods=["POST"])
def addprediction():
    try:
        # Extracting fields from the JSON request
        fullname = request.json.get("fullname")
        age = request.json.get("age")
        gender = request.json.get("gender")
        datetimeprediction = request.json.get("datetimeprediction")
        resultprediction = request.json.get("resultprediction")
        email = request.json.get("email")
        phoneno = request.json.get("phoneno")
        doctorid = request.json.get("doctorid")

        # Check if the email already exists
        # prediction_exists = Prediction.query.filter_by(doctorid=doctorid).first() is not None

        # if prediction_exists:
        #     return jsonify({"error": "Email already exists"}), 409

        # Creating a new patient
        new_prediction = Prediction(
            fullname=fullname,
            age=age,
            gender=gender,
            datetimeprediction=datetimeprediction,
            resultprediction=resultprediction,
            email=email,
            phoneno=phoneno,
            doctorid=doctorid,
        )

        # Adding and committing the new user to the database
        db.session.add(new_prediction)
        db.session.commit()

        return jsonify(
            {
                "message": "Prediction Added",
                "fullname": fullname,
                "age": age,
                "gender": gender,
                "datetimeprediction": datetimeprediction,
                "resultprediction": resultprediction,
                "email": email,
                "phoneno": phoneno,
                "doctorid": doctorid,
            }
        ), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image


MODEL = tf.keras.models.load_model("./models/TestModel.h5")
CLASS_NAMES = ["Osteoporosis", "Normal"]


@api.route("/predict", methods=["POST"])
def predict():
    file = request.files["file"]
    image = read_file_as_image(file.read())
    image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)
    img_batch = np.expand_dims(image / 255, 0)
    predictions = MODEL.predict(img_batch)

    print(predictions)

    if predictions > 0.5:
        predicted_class = "Osteoporosis"
    else:
        predicted_class = "Normal"

    confidence = np.max(predictions[0])
    return {"class": predicted_class, "confidence": float(confidence)}


@api.route("/predictdelete/<id>", methods=["DELETE"])
def predictdelete(id):
    predict = Prediction.query.get(id)
    db.session.delete(predict)
    db.session.commit()
    return prediction_schema.jsonify(predict)


@api.route("/listpredict", methods=["GET"])
def listpredict():
    all_predict = Prediction.query.all()
    results = predictions_schema.dump(all_predict)
    return jsonify(results)


@api.route("/listpredictdetails/<id>", methods=["GET"])
def listpredictdetails(id):
    predictdetails = Prediction.query.get(id)
    return prediction_schema.jsonify(predictdetails)


@api.route("/listpredict/<doctor_id>", methods=["GET"])
def listpredict_for_doctor(doctor_id):
    predictions = Prediction.query.filter_by(doctorid=doctor_id).all()
    results = predictions_schema.dump(predictions)
    return jsonify(results)


# TEST UPLOAD IMAGE

UPLOAD_FOLDER = "static/uploads"
api.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
api.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/upload", methods=["POST"])
def upload_file():
    if "files[]" not in request.files:
        resp = jsonify({"message": "No file part in the request", "status": "failed"})
        resp.status_code = 400
        return resp

    files = request.files.getlist("files[]")
    print(files)

    success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(api.config["UPLOAD_FOLDER"], filename))

            newFile = Images(title=filename)
            db.session.add(newFile)
            db.session.commit()

            success = True

        else:
            resp = jsonify({"message": "File type is not allowed", "status": "failed"})
            return resp

    if success:
        resp = jsonify({"message": "Files successfully uploaded", "status": "success"})
        resp.status_code = 201
        return resp

    return resp


@api.route("/images", methods=["GET"])
def images():
    all_images = Images.query.all()
    results = images_schema.dump(all_images)
    return jsonify(results)
