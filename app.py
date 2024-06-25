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
