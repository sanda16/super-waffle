from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    IntegerField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
    DataRequired,
    NumberRange,
)
from mole.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class CrimeForm(FlaskForm):
    CRIME_CHOICES = [
        ("Assault", "Assault"),
        ("Housebreaking", "Housebreaking"),
        ("Rape", "Rape"),
        ("Highjack", "Highjack"),
    ]
    crime_type = SelectField(
        "Type of Crime", choices=CRIME_CHOICES, validators=[DataRequired()]
    )
    location = StringField("Location", validators=[DataRequired()])
    day_of_week = SelectField(
        "Day of Week",
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ],
        validators=[DataRequired()],
    )
    hour = IntegerField("Hour", validators=[DataRequired(), NumberRange(min=0, max=23)])
    minute = IntegerField(
        "Minute", validators=[DataRequired(), NumberRange(min=0, max=59)]
    )
    submit = SubmitField("Submit")
