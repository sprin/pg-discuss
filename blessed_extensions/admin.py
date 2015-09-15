import flask_admin
import flask_login
from flask_admin.contrib import sqla
from flask import (
    redirect,
    url_for,
)

from pg_discuss import ext
from pg_discuss import models

class AdminExt(ext.AppExtBase):
    def init_app(self, app):
        admin = flask_admin.Admin(app, 'pg-discuss Administration',
                                  template_mode='bootstrap3',
                                  index_view=MyAdminIndexView())
        # Add views
        admin.add_view(CommentAdmin(models.Comment, models.db.session))
        admin.add_view(ThreadAdmin(models.Thread, models.db.session))
        admin.add_view(IdentityAdmin(models.Identity, models.db.session))

class AuthenticatedModelView(sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated()

class CommentAdmin(AuthenticatedModelView):
    pass

class ThreadAdmin(AuthenticatedModelView):
    pass

class IdentityAdmin(AuthenticatedModelView):
    pass

class MyAdminIndexView(flask_admin.AdminIndexView):

    @flask_admin.expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('admin_login'))
        return super(MyAdminIndexView, self).index()
