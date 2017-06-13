from os import getenv
from ast import literal_eval
from flask import Flask, redirect, url_for, render_template, flash, session, request
from functools import wraps
from utils import UtilSearch
from forms import LoginForm, SignupForm, \
    EmailResetPasswordForm, ResetPasswordForm, \
    SearchForm
from models import db, User, Search, OldSearch, NotificationHistory
from flask_mail import Mail, Message
from uuid import uuid4
from werkzeug.security import generate_password_hash, \
    check_password_hash
from datetime import datetime, date
from sqlalchemy import Date, cast

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

# STATIC
LIMIT_SEARCH = 5
LIMIT_RESULTS = 10
LIMIT_NOTIFYS = 10

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
    # Redirect App
    if request.args.get('app'):
        return redirect(
            'http://p.wallapop.com/i/{0}?_pid=web&_me=www&campaign=mobile_item'.format(
                request.args.get('app')))

    # Home
    return render_template('web/home.html')


@app.route('/robots.txt')
def robotstxt():
    return render_template('robots.txt')


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    '''
    Signup page
    '''
    # Redirigue to login if these logged in
    if 'user' in session:
        return redirect(url_for('dashboard'))
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
                'Activar cuenta',
                sender='no-reply@' + getenv('DOMAIN'),
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
                token=link,
                domain=getenv('DOMAIN')
            )
            try:
                # Save new User
                db.session.commit()
                # Send confirmation email
                mail.send(msg)
                # Informamos al usuario
                flash(
                    'Te acabamos de enviar un email para activar la cuenta. Si no lo encuentras en tu bandeja de entrada, revisa Spam.',
                    'warning')
                flash('¡Cuenta creada!', 'success')
                return redirect(url_for('login'))
            except BaseException:
                db.session.rollback()
                flash(
                    '''¡Ups! Algo ha pasado.
                    ¿Puedes volver a intentarlo?.''',
                    'danger'
                )
        else:
            flash('El email ya esta siendo utilizado.', 'danger')
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
        flash('¡Su cuenta ya esta activada!', 'success')
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
                'Recuperar contraseña',
                sender='no-reply@' + getenv('DOMAIN'),
                recipients=[form.email.data]
            )
            msg.body = render_template(
                'emails/forgot_password.txt', username=my_user.username,
                token=link
            )
            msg.html = render_template(
                'emails/forgot_password.html',
                username=my_user.username,
                token=link,
                domain=getenv('DOMAIN')
            )
            mail.send(msg)
            flash('''
            Le acabamos de enviar un email para resetear la contraseña.
            Si no lo encuentra, busque en su carpeta de Spam.
            ''', 'success')
            return redirect(url_for('login'))
        else:
            flash('El email no esta registrado.', 'danger')

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
            my_user.token = str(uuid4()).replace('-', '')
            # Update password
            db.session.add(my_user)
            db.session.commit()
            flash('¡Su contraseña se ha actualizado correctamente!', 'success')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))
    return render_template('web/update_password.html', form=form, email=email)


@app.route('/login', methods=('GET', 'POST'))
def login():
    '''
    Page login
    '''
    # Redirigue to login if these logged in
    if 'user' in session:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        # Validate email and password
        email = form.email.data
        my_user = User.query.filter_by(
            email=email).filter_by(is_active=1).first()
        if not my_user:
            flash(
                'No ha activado todavía su cuenta. Verifique su buzón.',
                'danger')
        else:
            if my_user and check_password_hash(
                    my_user.password,
                    form.password.data):
                # Login de usuario
                session['user'] = {
                    'id': my_user.id,
                    'username': my_user.username,
                    'email': my_user.email
                }
                return redirect(url_for('dashboard'))
            else:
                flash(
                    'El email o la contraseña es incorrecto. Por favor, vuelva a intentarlo.',
                    'danger')
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


@app.route('/panel/busquedas', methods=('GET', 'POST'))
@login_required
def dashboard():
    '''
    Page dashboard.
    Protected area. Only accessible with login.
    '''
    form = SearchForm()
    results = False
    util_search = UtilSearch()
    if request.method == 'POST':
        # Search
        if 'search' in request.form:
            if form.validate_on_submit():
                try:
                    results = util_search.get(
                        form.name.data,
                        request.form['lat'],
                        request.form['lng'],
                        request.form['distance'],
                        form.max_price.data
                        )
                except:
                    flash('Ha ocurrido un error al buscar. Por favor, vuelva a intentarlo.', 'danger')
        # Add
        elif 'add' in request.form:
            searchs = Search.query.filter_by(
                user_id=session['user']['id']).all()
            searchs_len = len(searchs)
            if searchs_len < LIMIT_SEARCH:
                # Search
                my_search = Search()
                my_search.name = request.form['add']
                my_search.lat = request.form['lat']
                my_search.lng = request.form['lng']
                my_search.distance = request.form['distance']
                my_search.max_price = form.max_price.data
                my_search.user_id = session['user']['id']
                db.session.add(my_search)
                db.session.flush()
                db.session.commit()
                # Old searchs
                results = util_search.get(
                        my_search.name,
                        my_search.lat,
                        my_search.lng,
                        my_search.distance,
                        form.max_price.data
                    )
                for item in results:
                    my_old = OldSearch()
                    my_old.item_id = item['itemId']
                    my_old.search_id = my_search.id
                    db.session.add(my_old)
                try:
                    db.session.commit()
                    flash(
                        '¡Wallaviso activado! Te avisaremos al instante con nuevos productos.',
                        'success')
                except BaseException:
                    db.session.rollback()
                    flash(
                        '''¡Ups! Algo ha pasado.
                        ¿Puedes volver a intentarlo?.''',
                        'danger'
                    )

                results = False
                form.name.data = ''
            else:
                flash(
                    'No puedes tener más de {limit} Wallavisos. ¿Por qué no borras una que no uses?'.format(
                        limit=LIMIT_SEARCH), 'danger')
        # Remove
        elif 'delete' in request.form:
            my_search = Search.query.filter_by(
                id=request.form['delete'],
                user_id=session['user']['id']
            ).first()
            db.session.delete(my_search)
            try:
                db.session.commit()
                flash(
                    '¡Wallaviso borrado!',
                    'success'
                )
            except BaseException:
                db.session.rollback()
                flash(
                    '''¡Ups! Algo ha pasado.
                    ¿Puedes volver a intentarlo?.''',
                    'danger'
                )
    searchs = Search.query.filter_by(user_id=session['user']['id']).all()
    searchs_len = len(searchs)
    num_notifys = NotificationHistory.query.filter_by(
        user_id=session['user']['id']
        ).filter(
            cast(NotificationHistory.create_at, Date) == date.today()
        ).count()
    return render_template(
        'web/dashboard/searchs.html',
        form=form,
        searchs=searchs,
        searchs_len=searchs_len,
        results=results,
        LIMIT_RESULTS=LIMIT_RESULTS,
        LIMIT_NOTIFYS=LIMIT_NOTIFYS,
        num_notifys=num_notifys
    )


@app.route('/update_expiration/<id>/<token>')
def update_expiration(id, token):
    '''
    Page update expiration
    '''
    my_search = Search.query.filter_by(
        id=id,
        token=token,
        alert_expiration=True
    ).first()
    if my_search:
        my_search.update_at = datetime.utcnow()
        my_search.alert_expiration = False
        db.session.add(my_search)
        try:
            db.session.commit()
            flash('¡Busqueda actualizada!', 'success')
        except:
            db.session.rollback()
            flash(
                '''¡Ups! Algo ha pasado.
                ¿Puedes volver a intentarlo?.''',
                'danger'
            )
    return redirect(url_for('index'))


@app.route('/panel/historial')
@login_required
def notify_history():
    histories = NotificationHistory.query.filter_by(
        user_id=session['user']['id']
        ).filter(
            cast(NotificationHistory.create_at, Date) == date.today()
        ).all()
    return render_template('web/dashboard/histories.html', histories=histories)



# END VIEWS

# MAIN

if __name__ == "__main__":
    app.run(host="0.0.0.0")
# END MAIN
