from os import getenv
from ast import literal_eval
from flask import Flask, redirect, url_for, render_template, flash, session
from functools import wraps
from forms import LoginForm, SignupForm, \
        EmailResetPasswordForm, ResetPasswordForm
from models import db, User
from flask_mail import Mail, Message
from uuid import uuid4
from werkzeug.security import generate_password_hash, \
     check_password_hash

# CONFIGURATIONS
# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['DEBUG'] = literal_eval(getenv('DEBUG'))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Email
app.config['MAIL_SERVER'] = getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME', None)
app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD', None)
app.config['MAIL_PORT'] = getenv('MAIL_PORT')

mail = Mail(app)

# END CONFIGURATIONS

# DECORATIONS


def login_required(f):
    # Decoration: check login in session
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            session.clear()
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# END DECORATIONS

# VIEWS


@app.route('/')
def index():
    '''
    Index page
    '''
    return render_template('web/home.html')


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    '''
    Signup page
    '''
    form = SignupForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email=form.email.data).all():
            my_user = User()
            form.populate_obj(my_user)
            # Encrypt password
            my_user.password = generate_password_hash(form.password.data)
            db.session.add(my_user)
            # Prepare the account activation email
            msg = Message(
                'Activate account',
                sender='no-repy@' + getenv('DOMAIN'),
                recipients=[my_user.email]
                )
            link = 'http://' + getenv('DOMAIN') + url_for(
                'activate_account',
                token=my_user.token
                )
            msg.body = render_template(
                'emails/activate.txt', username=my_user.username,
                token=link
                )
            msg.html = render_template(
                'emails/activate.html',
                username=my_user.username,
                token=link
                )
            try:
                # Save new User
                db.session.commit()
                # Send confirmation email
                mail.send(msg)
                # Informamos al usuario
                flash('Account created successfully.', 'success')
                flash('We have sent you a confirmation email.', 'warning')
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash(
                    '''We're sorry, an internal error has occurred.
                    Please, try again.''',
                    'danger'
                    )
        else:
            flash('Email exists.', 'danger')
    return render_template('web/signup.html', form=form)


@app.route('/activate/<token>')
def activate_account(token):
    '''
    Activate account
    '''
    # Obtenemos el usuario que tenga ese token
    my_user = User.query.filter_by(token=token).first()
    if my_user:
        # Lo activamos
        my_user.is_active = True
        db.session.add(my_user)
        db.session.commit()
        # Mostramos mensaje
        flash('Your account has been activated.', 'success')
    return redirect(url_for('login'))


@app.route('/forgot_password/new', methods=('GET', 'POST'))
def forgot_password():
    '''
    Page lost password
    '''
    form = EmailResetPasswordForm()
    if form.validate_on_submit():
        # Check if the email is in the database
        my_user = User.query.filter_by(email=form.email.data).first()
        if my_user:
            # Generate new token
            token = str(uuid4()).replace('-', '')
            # Update user token
            my_user.token = token
            db.session.add(my_user)
            db.session.commit()
            # Send email with token
            link = 'http://' + getenv('DOMAIN') + url_for(
                    'update_password',
                    email=my_user.email, token=token
                    )
            msg = Message(
                'Recover password',
                sender='no-repy@' + getenv('DOMAIN'),
                recipients=[form.email.data]
                )
            msg.body = render_template(
                'emails/forgot_password.txt', username=my_user.username,
                token=link
                )
            msg.html = render_template(
                'emails/forgot_password.html',
                username=my_user.username,
                token=link
                )
            mail.send(msg)
            flash('''
            We have sent an email to change your password.
            Please check your Spam folder if not found.
            ''', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email is not registered.', 'danger')

    return render_template('web/forgot_password.html', form=form)


@app.route('/forgot_password/update/<email>/<token>', methods=('GET', 'POST'))
def update_password(email, token):
    '''
    Page update password
    '''
    form = ResetPasswordForm()
    # Check that the user is valid
    my_user = User.query.filter_by(email=email, token=token).first()
    if my_user:
        if form.validate_on_submit():
            # Encrypt password
            my_user.password = generate_password_hash(form.password.data)
            # Update password
            db.session.add(my_user)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))
    return render_template('web/update_password.html', form=form, email=email)


@app.route('/login', methods=('GET', 'POST'))
def login():
    '''
    Page login
    '''
    form = LoginForm()
    if form.validate_on_submit():
        # Validate email and password
        email = form.email.data
        my_user = User.query.filter_by(email=email).first()
        if my_user and check_password_hash(
                my_user.password,
                form.password.data):
            # Login de usuario
            session['user'] = my_user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Your email or password is not valid.', 'danger')
    return render_template('web/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    '''
    Page logout
    '''
    # Clear sessions
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    '''
    Page dashboard.
    Protected area. Only accessible with login.
    '''
    return render_template('web/dashboard.html')

# END VIEWS

# MAIN


if __name__ == "__main__":
    app.run()
# END MAIN
