from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, StringField, PasswordField, validators, SubmitField

class FormRegister(FlaskForm):
    """依照Model來建置相對應的Form

    password2: 用來確認兩次的密碼輸入相同
    """

    account = StringField('Account', validators=[
        validators.DataRequired(),
    ])

    password = PasswordField('PassWord', validators=[
        validators.DataRequired(),
        validators.EqualTo('password2', message='PASSWORD NEED MATCH')
    ])
    password2 = PasswordField('Confirm PassWord', validators=[
        validators.DataRequired()
    ])

    username = StringField('UserName', validators=[
        validators.DataRequired(),
    ])

    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])

    submit = SubmitField('Register New Account')

class MessageForm(FlaskForm):
    message = StringField('Message', validators=[
        validators.DataRequired(),
    ])

class FormLogin(FlaskForm):
    account = StringField('Account', validators=[
        validators.DataRequired(),
    ])

    password = PasswordField('PassWord', validators=[
        validators.DataRequired(),
    ])
    submit = SubmitField('Log in')