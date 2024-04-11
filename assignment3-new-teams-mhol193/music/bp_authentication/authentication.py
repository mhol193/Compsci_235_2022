from flask import Blueprint, render_template, redirect, url_for, session, make_response, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from password_validator import PasswordValidator

from functools import wraps

import music.bp_authentication.services as services
import music.adapters.a_repository as repo

# !!!!!! change redirect url to home page once made (find below)

# Configure Blueprint.
authentication_blueprint = Blueprint(
    'bp_authentication', __name__, url_prefix='/authentication')



@authentication_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    user_name_not_unique = None

    if form.validate_on_submit():
        # Successful POST, i.e. the user name and password have passed validation checking.
        # Use the service layer to attempt to add the new user.
        try:
            services.add_user(form.user_name.data, form.password.data, repo.repo_instance)
            # All is well, redirect the user to the login page.
            return redirect(url_for('bp_authentication.login'))
        except services.NameNotUniqueException:
            user_name_not_unique = 'Your user name is already taken - please supply another'
    
    return render_template(
        'authentication/credentials.html',
        title='Register',
        form=form,
        user_name_error_message=user_name_not_unique,
        handler_url=url_for('bp_authentication.register'))


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name_not_recognised = None
    password_does_not_match_user_name = None

    if request.method == 'POST':
        if form.validate_on_submit():
            # Successful POST, i.e. the user name and password have passed validation checking.
            # Use the service layer to lookup the user.
            try:
                user = services.get_user(form.user_name.data, repo.repo_instance)

                # Authenticate user.
                services.authenticate_user(user['user_name'], form.password.data, repo.repo_instance)
                
                # Initialise session and redirect the user to the friends page. 
                session.clear()
                session['user_name'] = user['user_name']
                session['profile_photo'] = user['profile_photo']

                response = redirect(url_for('bp_browse.list_tracks', page_num = 1))
                # response.headers.set('Location', '/alltracks1')
                return response

            except services.UnknownUserException:
                # User name not known to the system, set a suitable error message.
                user_name_not_recognised = '*This username does not exist.'

            except services.AuthenticationException:
                # Authentication failed, set a suitable error message.
                password_does_not_match_user_name = '*Wrong password - please try again'

    # For a GET or a failed POST, return the Login Web page.
    return render_template(
        'authentication/credentials.html',
        title='Login',
        user_name_error_message=user_name_not_recognised,
        password_error_message=password_does_not_match_user_name,
        form=form,
    )


@authentication_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp_authentication.login'))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            return redirect(url_for('bp_authentication.login'))
        return view(**kwargs)
    return wrapped_view


class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = u'Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8) \
            .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    user_name = StringField('Username', [
        DataRequired(message='Username is required'),
        Length(min=3, max=6, message='Username has to be between 3 and 6 characters'),])
    password = PasswordField('Password', [
        DataRequired(message='Password is required'),
        PasswordValid()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    user_name = StringField('Username', [
        DataRequired()])
    password = PasswordField('Password', [
        DataRequired()])
    submit = SubmitField('Login')