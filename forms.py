from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    '''
    Form Login
    '''
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
            ]
        )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
            ]
        )


class SignupForm(FlaskForm):
    '''
    Form signup
    '''
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(5, 30, '''
            You can not have less than 5 characters or more 30.
            ''')
            ]
        )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(1, 254, 'Too long.')
            ]
        )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo(
                'password_confirm',
                'Passwords are not the same.'
                )
            ]
        )
    password_confirm = PasswordField('Repeat password')
    accept_tos = BooleanField(
        'I accept the terms and conditions.',
        validators=[
            DataRequired('Please accept the terms and conditions.')
            ]
        )


class EmailResetPasswordForm(FlaskForm):
    '''
    Form send email reset password
    '''
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
            ]
        )


class ResetPasswordForm(FlaskForm):
    '''
    Form update password
    '''
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo(
                'password_confirm',
                'Passwords are not the same.'
                )
            ]
        )
    password_confirm = PasswordField('Repeat password')
