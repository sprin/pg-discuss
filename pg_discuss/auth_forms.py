import getpass
from wtforms import fields, validators
import wtforms
import flask_wtf
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.script import Command

from . import models
from .models import db

# Define login and registration forms (for flask-login)
class LoginForm(flask_wtf.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return models.db.session.query(models.AdminUser).filter_by(login=self.login.data).first()

class RegistrationForm(wtforms.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if models.db.session.query(models.AdminUser).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

class CreateAdminUser(Command):

    def run(self):
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
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)
            user.active = True

            db.session.add(user)
            db.session.commit()
        else:
            print(form.errors)
