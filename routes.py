from app import api, db, bcrypt
from models import Doctor, Users, Admin
from schemas import UserSchema, DoctorSchema
from flask import jsonify, request
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity

user_schema = UserSchema()
users_schema = UserSchema(many=True)

doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)

@api.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


#PATIENTS

@api.route('/listusers',methods = ['GET'])
def listusers():
    all_users = Users.query.all()
    results = users_schema.dump(all_users)
    return jsonify(results)

@api.route('/userdetails/<id>',methods = ['GET'])
def userdetails(id):
    user = Users.query.get(id)
    return user_schema.jsonify(user)

@api.route('/userupdate/<id>',methods = ['PUT'])
def userupdate(id):
    user = Users.query.get(id)

    name = request.json['name']
    email = request.json['email']

    user.name = name
    user.email = email

    db.session.commit()
    return user_schema.jsonify(user)

@api.route('/userdelete/<id>',methods = ['DELETE'])
def userdelete(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


@api.route("/useradd", methods=['POST'])
def useradd():
    try:
        name = request.json['name']
        email = request.json['email']

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

#DOCTORS

@api.route('/logintokendoctors', methods=["POST"])
def create_token():

    data = request.get_json()
    email = data['email']
    password = data['password']
    print('Received data:', email , password)

    doctor = Doctor.query.filter_by(email=email).first()

    if doctor and bcrypt.check_password_hash(doctor.password, password):
        access_token = create_access_token(identity=doctor.id)
        return jsonify({'message': 'Login Success', 'doctor_token': access_token, 'email': email})
    else:
        return jsonify({'message': 'Login Failed'}), 401

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
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Creating a new doctor user
        new_user = Doctor(username=username, email=email, password=hashed_password, fullname=fullname, phoneno=phoneno)
        
        # Adding and committing the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User successfully signed up",
            "email": email
        }), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500


    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Return the error message
        return jsonify({"error": str(e)}), 500
    
@api.route('/listdoctors',methods = ['GET'])
def listdoctors():
    all_doctors = Doctor.query.all()
    results = doctors_schema.dump(all_doctors)
    return jsonify(results)

@api.route('/doctordetails/<id>',methods = ['GET'])
def doctordetails(id):
    doctor = Doctor.query.get(id)
    return doctor_schema.jsonify(doctor)

@api.route('/doctorupdate/<id>',methods = ['PUT'])
def doctorupdate(id):
    doctor = Doctor.query.get(id)

    fullname = request.json['fullname']
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    phoneno = request.json['phoneno']

    if fullname:
        doctor.fullname = fullname
    if username:
        doctor.username = username
    if email:
        doctor.email = email
    if password:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
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
    
@api.route('/profile/<getemail>')
def my_profile(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    
    doctor = Doctor.query.filter_by(email=getemail).first()

    response_body = {
        "id": doctor.id,
        "name": doctor.username,
        "email": doctor.email,
        "fullname" : doctor.fullname,
        "phoneno" : doctor.phoneno
    }

    return response_body

#ADMIN

@api.route('/logintokenadmin', methods=["POST"])
def create_token_admin():

    data = request.get_json()
    email = data['email']
    password = data['password']
    print('Received data:', email , password)

    admin = Admin.query.filter_by(email=email).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        access_token = create_access_token(identity=admin.id)
        return jsonify({'message': 'Login Success', 'admin_token': access_token, 'email': email})
    else:
        return jsonify({'message': 'Login Failed'}), 401

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

    return jsonify({
        "message": "User successfully signed up",
        "email": email
    }), 201

@api.route("/logoutadmin", methods=["POST"])
def logoutadmin():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
    
@api.route('/profileadmin/<getemail>')
@jwt_required()
def my_profile_admin(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    
    admin = Admin.query.filter_by(email=getemail).first()

    response_body = {
        "id": admin.id,
        "name": admin.username,
        "email": admin.email,
    }

    return response_body

@api.route('/doctordelete/<id>',methods = ['DELETE'])
def doctordelete(id):
    doctor = Doctor.query.get(id)
    db.session.delete(doctor)
    db.session.commit()
    return doctor_schema.jsonify(doctor)