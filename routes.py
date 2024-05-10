from app import api, db, bcrypt
from models import Doctor, Users
from schemas import UserSchema
from flask import jsonify, request
from flask_jwt_extended import create_access_token, unset_jwt_cookies, jwt_required, get_jwt_identity

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@api.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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

@api.route('/logintoken', methods=["POST"])
def create_token():

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    doctor = Doctor.query.filter_by(email=email).first()

    # if email != "test" or password != "test":
    #     return {"msg": "Wrong email or password"}, 401

    if doctor is None:
        return jsonify({"error": "Wrong email or password"}), 401
    
    if not bcrypt.check_password_hash(doctor.password, password):
        return jsonify ({"error": "Unauthorized"}), 401

    access_token = create_access_token(identity=email)
    # response =  {"access_token": access_token}

    return jsonify({
        "email": email,
        "access_token": access_token
    })
    # return response

@api.route("/signup", methods=["POST"])
def signup():
    email = request.json["email"]
    password = request.json["password"]

    user_exists = Doctor.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Email already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = Doctor(name="doctor3", email=email, password=hashed_password, about="sample about doctor3")
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User successfully signed up",
        "email": email
    }), 201
    
@api.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
    
@api.route('/profile/<getemail>')
@jwt_required()
def my_profile(getemail):
    print(getemail)
    if not getemail:
        return jsonify({"error": "Unauthorized Access"}), 401
    
    doctor = Doctor.query.filter_by(email=getemail).first()

    response_body = {
        "id": doctor.id,
        "name": doctor.name,
        "email": doctor.email,
        "about": doctor.about,
    }

    return response_body