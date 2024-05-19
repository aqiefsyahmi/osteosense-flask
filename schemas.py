from app import ma

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "name", "email", "date")

class DoctorSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "username", "email", "password",  "fullname", "phoneno")

