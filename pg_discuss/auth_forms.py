"""Form for Admin login and a Flask-Script command to set up an Admin user from
the command line.
"""
import getpass

import flask_script
import flask_wtf
import werkzeug
import wtforms

from . import models
from .db import db


class LoginForm(flask_wtf.Form):
    """Login form for Admin users."""
    login = wtforms.fields.TextField(
        validators=[wtforms.validators.DataRequired()])
    password = wtforms.fields.PasswordField(
        validators=[wtforms.validators.DataRequired()])

    def validate_login(self, field):
        """Validate that user is valid and password matches stored hash."""
        user = self.get_user()

        if user is None:
            raise wtforms.validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not werkzeug.check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise wtforms.validators.ValidationError('Invalid password')

    def get_user(self):
        """Get the user object associated with the login."""
        return (
            db.session.query(models.AdminUser)
            .filter_by(login=self.login.data).first()
        )


class RegistrationForm(wtforms.Form):
    """Registration form to validate new Admin user data."""
    login = wtforms.fields.TextField(
        validators=[wtforms.validators.DataRequired()])
    email = wtforms.fields.TextField()
    password = wtforms.fields.PasswordField(
        validators=[wtforms.validators.DataRequired()])

    def validate_login(self, field):
        """Validate that login does not already exist."""
        if (
            db.session.query(models.AdminUser)
            .filter_by(login=self.login.data).count() > 0
        ):
            raise wtforms.validators.ValidationError('Duplicate username')


class CreateAdminUser(flask_script.Command):
    """Flask-Script command to create a new Admin user."""

    def run(self):
        """Create a new Admin user."""
        login = None
        password = None
        email = None

        while login is None:
            login = input('Login name: ')

        while email is None:
            email = input('Email: ')

        while password is None:
            password = getpass.getpass()
            password2 = getpass.getpass('Password (again): ')
            if password != password2:
                print("Error: Your passwords didn't match.")
                password = None
                # Don't validate passwords that don't match.
                continue

            if password.strip() == '':
                print("Error: Blank passwords aren't allowed.")
                password = None
                # Don't validate blank passwords.
                continue

        form = RegistrationForm(login=login, email=email,
                                password=password)
        if form.validate():
            user = models.AdminUser()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the
            # db.
            user.password = werkzeug.generate_password_hash(form.password.data)
            user.active = True

            db.session.add(user)
            db.session.commit()
        else:
            print(form.errors)
