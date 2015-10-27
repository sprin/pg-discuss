import flask
import flask_admin
import flask_admin.contrib.sqla
import flask_admin.contrib.sqla.form
import flask_login
import os
import jinja2
import simplejson as json
import sqlalchemy.orm
import wtforms.fields
import werkzeug.utils

from pg_discuss import ext
from pg_discuss import models

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class AdminExt(ext.AppExtBase):
    """Extension to add an admin interface. Allows management of Comment,
    Thread, Identity, and AdminUser models.

    Available to authenticated Admin users.
    """
    def init_app(self, app):
        # Add template loader
        my_loader = jinja2.ChoiceLoader([
            app.jinja_loader,
            jinja2.FileSystemLoader(THIS_DIR),
        ])
        app.jinja_loader = my_loader

        # Add static file route. The web server should be configured to serve
        # static files, not the app, but we do it here to allow the files
        # to be served without additional web server config.
        app.route('/admin_static/<path:filename>', methods=['GET'])(
            self.admin_static)

        # Configure Admin
        admin = flask_admin.Admin(app, 'pg-discuss Administration',
                                  template_mode='bootstrap3',
                                  base_template='admin_templates/base.html',
                                  index_view=MyAdminIndexView())
        app.admin = admin
        # Add views
        admin.add_view(CommentAdmin(PrettyComment, models.db.session,
                                    name='Comment'))
        admin.add_view(ThreadAdmin(models.Thread, models.db.session))
        admin.add_view(IdentityAdmin(PrettyIdentity, models.db.session,
                                     name='Identity'))
        admin.add_view(AdminUserAdmin(models.AdminUser, models.db.session))

        # Set up login callback.
        app.login_callback = (
            lambda: flask.redirect(flask.url_for('admin.index')))

    def admin_static(self, filename):
        return flask.send_from_directory(
            THIS_DIR + '/admin_static/',
            werkzeug.utils.secure_filename(filename))


class PrettyIdentity(models.Identity):
    """Subclass the Identity model to provide a nicer string represention."""
    def __unicode__(self):
        names = self.custom_json.get('names')
        remote_addrs = self.custom_json.get('remote_addrs')
        if names:
            str_ = names[0]
        elif remote_addrs:
            str_ = remote_addrs[0]
        else:
            str_ = '?'
        return "({}) {}".format(self.id, str_)
    __str__ = __unicode__


class PrettyComment(models.Comment):
    """Subclass the Identity model to provide a nicer string represention."""
    identity_ = sqlalchemy.orm.relationship('PrettyIdentity')


class AuthenticatedModelView(flask_admin.contrib.sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return flask.redirect(flask.url_for('admin_login'))


class DictToJSONField(wtforms.fields.TextAreaField):
    def process_data(self, value):
        if value is None:
            value = {}

        self.data = json.dumps(value, sort_keys=True,
                               indent=4, separators=(',', ': '))

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = json.loads(valuelist[0])
        else:
            self.data = '{}'


class CustomAdminConverter(flask_admin.contrib.sqla.form.AdminModelConverter):
    @flask_admin.contrib.sqla.form.converts('JSON')
    def conv_JSON(self, field_args, **extra):
        return DictToJSONField(**field_args)


class CommentAdmin(AuthenticatedModelView):
    model_form_converter = CustomAdminConverter
    column_exclude_list = ['identity']
    form_excluded_columns = ['identity']
    form_widget_args = {
        'custom_json': {'rows': 10}
    }


class ThreadAdmin(AuthenticatedModelView):
    model_form_converter = CustomAdminConverter
    form_widget_args = {
        'custom_json': {'rows': 10}
    }


class IdentityAdmin(AuthenticatedModelView):
    model_form_converter = CustomAdminConverter
    form_widget_args = {
        'custom_json': {'rows': 10}
    }


class AdminUserAdmin(AuthenticatedModelView):
    pass


class MyAdminIndexView(flask_admin.AdminIndexView):

    @flask_admin.expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('admin_login'))
        return super(MyAdminIndexView, self).index()
