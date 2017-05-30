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
            DataRequired('Campo obligatorio'),
            Email('Formato no válido')
            ]
        )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired('Campo obligatorio')
            ]
        )


class SignupForm(FlaskForm):
    '''
    Form signup
    '''
    username = StringField(
        'Nombre de usuario',
        validators=[
            DataRequired('Campo obligatorio'),
            Length(5, 30, '''
                Debe tener entre 5 y 30 carácteres.
            ''')
            ]
        )
    email = StringField(
        'Email',
        validators=[
            DataRequired('Campo obligatorio'),
            Email('No tiene un formato válido.'),
            Length(1, 254, 'Demasiado largo.')
            ]
        )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired('Campo obligatorio'),
            EqualTo(
                'password_confirm',
                'Las contraseñas no coinciden.'
                )
            ]
        )
    password_confirm = PasswordField('Repite la contraseña')

class EmailResetPasswordForm(FlaskForm):
    '''
    Form send email reset password
    '''
    email = StringField(
        'Email',
        validators=[
            DataRequired('Campo obligatorio'),
            Email('Formato no válido')
            ]
        )


class ResetPasswordForm(FlaskForm):
    '''
    Form update password
    '''
    password = PasswordField(
        'Nueva contraseña',
        validators=[
            DataRequired('Campo obligatorio'),
            EqualTo(
                'password_confirm',
                'No son iguales.'
                )
            ]
        )
    password_confirm = PasswordField('Repetir contraseña')

class SearchForm(FlaskForm):
    '''
    Form search item
    '''
    name = StringField(
        'Nombre',
        validators=[
            DataRequired('Campo obligatorio'),
            Length(1, 100, 'Demasiado largo.')
            ],
        render_kw={"placeholder": "Buscar..."}
        )


