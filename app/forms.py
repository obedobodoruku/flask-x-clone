from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import EqualTo, DataRequired, ValidationError, Length, Email
from app.models import  db, User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken")
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("This email is already taken")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class CreatePostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")

class ReplyForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Reply")

class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    name = StringField("Name")
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken")
        
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("This email is already taken")
        
class UpdatePostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Reply")

class UpdateReplyForm(FlaskForm):
    content = TextAreaField("Content")
    submit = SubmitField("Update")