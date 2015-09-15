import flask_admin
import flask_login
from flask_admin.contrib import sqla
from flask import (
    redirect,
    url_for,
)

from pg_discuss import ext
from pg_discuss import models
from sqlalchemy.orm import relationship

class AdminExt(ext.AppExtBase):
    def init_app(self, app):
        admin = flask_admin.Admin(app, 'pg-discuss Administration',
                                  template_mode='bootstrap3',
                                  index_view=MyAdminIndexView())
        # Add views
        admin.add_view(CommentAdmin(PrettyComment, models.db.session,
                                    name='Comment'))
        admin.add_view(ThreadAdmin(models.Thread, models.db.session))
        admin.add_view(IdentityAdmin(PrettyIdentity, models.db.session,
                                     name='Identity'))
        admin.add_view(AdminUserAdmin(models.AdminUser, models.db.session))

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
    identity = relationship('PrettyIdentity')


class AuthenticatedModelView(sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated()

class CommentAdmin(AuthenticatedModelView):
    pass

class ThreadAdmin(AuthenticatedModelView):
    pass

class IdentityAdmin(AuthenticatedModelView):
    pass

class AdminUserAdmin(AuthenticatedModelView):
    pass

class MyAdminIndexView(flask_admin.AdminIndexView):

    @flask_admin.expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('admin_login'))
        return super(MyAdminIndexView, self).index()
