from app import ma


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "name", "email", "date")


class AdminSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "username", "email", "password")


class DoctorSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "username", "email", "password", "fullname", "phoneno")


class PatientSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            "id",
            "fullname",
            "age",
            "gender",
            "email",
            "phoneno",
        )


class PredictionSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            "id",
            "fullname",
            "age",
            "gender",
            "datetimeprediction",
            "resultprediction",
            "email",
            "phoneno",
            "doctorid",
            "imageprediction",
        )


class ImageSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            "id",
            "title",
        )
