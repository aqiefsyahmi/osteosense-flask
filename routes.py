from io import BytesIO
from unittest import result
from PIL import Image
import cv2
import numpy as np
from sqlalchemy import false, func
import tensorflow as tf

# for image
import os
import urllib.request
from werkzeug.utils import secure_filename

from app import api, db, bcrypt
from models import Doctor, Users, Admin, Patient, Prediction
from schemas import (
    UserSchema,
    AdminSchema,
    DoctorSchema,
    PatientSchema,
    PredictionSchema,
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


@api.route("/signupdoctormany", methods=["POST"])
def signupdoctormany():
    try:
        # Extracting the list of users from the JSON request
        users = request.json

        # List to collect any errors encountered during processing
        errors = []
        successful_signups = []

        for user in users:
            email = user.get("email")
            username = user.get("username")
            password = user.get("password")
            fullname = user.get("fullname")
            phoneno = user.get("phoneno")

            # Check if the email already exists
            user_exists = Doctor.query.filter_by(email=email).first() is not None

            if user_exists:
                errors.append({"email": email, "error": "Email already exists"})
                continue

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
            successful_signups.append(email)

        db.session.commit()

        return jsonify(
            {
                "message": "Users processed",
                "successful_signups": successful_signups,
                "errors": errors,
            }
        ), 201

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


@api.route("/countdoctors", methods=["GET"])
def countdoctors():
    doctor_count = db.session.query(func.count(Doctor.id)).scalar()
    return jsonify({"doctor_count": doctor_count})


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


@api.route("/profile/<getId>")
def my_profile(getId):
    print(getId)
    if not getId:
        return jsonify({"error": "Unauthorized Access"}), 401

    doctor = Doctor.query.filter_by(id=getId).first()

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


@api.route("/profileadmin/<getId>")
def my_profile_admin(getId):
    print(getId)
    if not getId:
        return jsonify({"error": "Unauthorized Access"}), 401

    admin = Admin.query.filter_by(id=getId).first()

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
        # Log the incoming request data
        print("Incoming request data:", request.json)

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
        # Log the error
        print("Error occurred:", str(e))

        # Rollback the session in case of an error
        db.session.rollback()

        # Return the error message
        return jsonify({"error": str(e)}), 500


@api.route("/listpatients", methods=["GET"])
def listpatients():
    all_patients = Patient.query.all()
    results = patients_schema.dump(all_patients)
    return jsonify(results)


@api.route("/countpatients", methods=["GET"])
def countpatients():
    patient_count = db.session.query(func.count(Patient.id)).scalar()
    return jsonify({"patient_count": patient_count})


@api.route("/countpatients/<gender>", methods=["GET"])
def count_patients_by_gender(gender):
    count = Patient.query.filter_by(gender=gender).count()
    return jsonify({"gender": gender, "count": count})


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
        imageprediction = request.json.get("imageprediction")

        # Creating a new prediction
        new_prediction = Prediction(
            fullname=fullname,
            age=age,
            gender=gender,
            datetimeprediction=datetimeprediction,
            resultprediction=resultprediction,
            email=email,
            phoneno=phoneno,
            doctorid=doctorid,
            imageprediction=imageprediction,
        )

        # Adding and committing the new prediction to the database
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
                "imageprediction": imageprediction,
            }
        ), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


# MANY PREDICTION INPUT TEST
# @api.route("/addlistpredictionmany", methods=["POST"])
# def addlistpredictionmany():
#     try:
#         # Extracting the list of predictions from the JSON request
#         predictions = request.json

#         # Checking if predictions is a list
#         if not isinstance(predictions, list):
#             return jsonify({"error": "Input should be a list of predictions"}), 400

#         # Creating a list to store new predictions
#         new_predictions = []

#         for prediction in predictions:
#             fullname = prediction.get("fullname")
#             age = prediction.get("age")
#             gender = prediction.get("gender")
#             datetimeprediction = prediction.get("datetimeprediction")
#             resultprediction = prediction.get("resultprediction")
#             email = prediction.get("email")
#             phoneno = prediction.get("phoneno")
#             doctorid = prediction.get("doctorid")
#             imageprediction = prediction.get("imageprediction")

#             # Creating a new prediction object
#             new_prediction = Prediction(
#                 fullname=fullname,
#                 age=age,
#                 gender=gender,
#                 datetimeprediction=datetimeprediction,
#                 resultprediction=resultprediction,
#                 email=email,
#                 phoneno=phoneno,
#                 doctorid=doctorid,
#                 imageprediction=imageprediction,
#             )

#             # Adding the new prediction to the list
#             new_predictions.append(new_prediction)

#         # Adding and committing the new predictions to the database
#         db.session.bulk_save_objects(new_predictions)
#         db.session.commit()

#         return jsonify({"message": f"{len(new_predictions)} predictions added"}), 201

#     except Exception as e:
#         # Rollback the session in case of an error
#         db.session.rollback()
#         # Return the error message
#         return jsonify({"error": str(e)}), 500


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image


MODEL = tf.keras.models.load_model("./models/TestModel.h5")
CLASS_NAMES = ["Osteoporosis", "Normal"]

UPLOAD_FOLDER = "static/uploads"
api.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
api.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_file_imgpred(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        resp = jsonify({"message": "No file part in the request", "status": "failed"})
        resp.status_code = 400
        return resp

    file = request.files["file"]

    if file and allowed_file_imgpred(file.filename):
        try:
            # Read the image file
            image_data = file.read()
            image = read_file_as_image(image_data)

            # Resize and normalize the image
            image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)
            img_batch = np.expand_dims(image / 255.0, axis=0)

            # Predict using the model
            predictions = MODEL.predict(img_batch)

            # Check the predictions and determine the class
            if predictions[0][0] > 0.5:
                predicted_class = "Osteoporosis"
            else:
                predicted_class = "Normal"

            confidence = float(predictions[0][0])

            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(api.config["UPLOAD_FOLDER"], filename)
            with open(file_path, "wb") as f:
                f.write(image_data)

            # Return the prediction result
            return jsonify(
                {
                    "class": predicted_class,
                    "confidence": confidence,
                    "imageprediction": filename,
                    "status": "success",
                }
            ), 201

        except Exception as e:
            resp = jsonify(
                {"message": f"Error processing file: {str(e)}", "status": "failed"}
            )
            resp.status_code = 500
            return resp

    else:
        resp = jsonify({"message": "File type is not allowed", "status": "failed"})
        resp.status_code = 400
        return resp


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


@api.route("/countpredics", methods=["GET"])
def countpredics():
    predict_count = db.session.query(func.count(Prediction.id)).scalar()
    return jsonify({"predict_count": predict_count})


@api.route("/countpredics/<resultprediction>", methods=["GET"])
def count_patients_by_and_condition(resultprediction):
    count = Prediction.query.filter_by(resultprediction=resultprediction).count()
    return jsonify({"resultprediction": resultprediction, "count": count})


@api.route("/countpredics/<gender>/<resultprediction>", methods=["GET"])
def count_patients_by_gender_and_condition(gender, resultprediction):
    count = Prediction.query.filter_by(
        gender=gender, resultprediction=resultprediction
    ).count()
    return jsonify(
        {"gender": gender, "resultprediction": resultprediction, "count": count}
    )


@api.route("/listpredictdetails/<id>", methods=["GET"])
def listpredictdetails(id):
    predictdetails = Prediction.query.get(id)
    return prediction_schema.jsonify(predictdetails)


@api.route("/listpredict/<doctor_id>", methods=["GET"])
def listpredict_for_doctor(doctor_id):
    predictions = Prediction.query.filter_by(doctorid=doctor_id).all()
    results = predictions_schema.dump(predictions)
    return jsonify(results)


@api.route("/doctor_with_predictions/<doctor_id>", methods=["GET"])
def doctor_with_predictions(doctor_id):
    # Fetch doctor details
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    # Fetch predictions for the doctor
    predictions = Prediction.query.filter_by(doctorid=doctor_id).all()

    # Serialize the doctor and predictions data
    doctor_data = doctor_schema.dump(doctor)
    predictions_data = predictions_schema.dump(predictions)

    # Count the number of predictions
    predictions_count = len(predictions)

    # Count the number of predictions for osteoporosis and normal
    osteoporosis_count = len(
        [p for p in predictions if p.resultprediction == "Osteoporosis"]
    )
    normal_count = len([p for p in predictions if p.resultprediction == "Normal"])

    # Count the number of predictions for normal and osteoporosis for male and female
    normal_male_count = len(
        [
            p
            for p in predictions
            if p.resultprediction == "Normal" and p.gender == "male"
        ]
    )
    osteo_male_count = len(
        [
            p
            for p in predictions
            if p.resultprediction == "Osteoporosis" and p.gender == "male"
        ]
    )
    normal_female_count = len(
        [
            p
            for p in predictions
            if p.resultprediction == "Normal" and p.gender == "female"
        ]
    )
    osteo_female_count = len(
        [
            p
            for p in predictions
            if p.resultprediction == "Osteoporosis" and p.gender == "female"
        ]
    )

    # Combine the data into a single response
    response = {
        "doctor": doctor_data,
        "predictions": predictions_data,
        "predictions_count": predictions_count,
        "osteoporosis_count": osteoporosis_count,
        "normal_count": normal_count,
        "normal_male_count": normal_male_count,
        "osteo_male_count": osteo_male_count,
        "normal_female_count": normal_female_count,
        "osteo_female_count": osteo_female_count,
        "male_count": normal_male_count + osteo_male_count,
        "female_count": normal_female_count + osteo_female_count,
    }

    return jsonify(response)


@api.route("/listdoctorswithcount", methods=["GET"])
def listdoctorswithcount():
    all_doctors = Doctor.query.all()
    results = doctors_schema.dump(all_doctors)

    for doctor in results:
        doctor_id = doctor["id"]
        predict_count = (
            db.session.query(func.count(Prediction.id))
            .filter_by(doctorid=doctor_id)
            .scalar()
        )
        doctor["predict_count"] = predict_count

    return jsonify(results)
