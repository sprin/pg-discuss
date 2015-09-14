import flask_admin
from flask_admin.contrib import sqla

from pg_discuss import ext
from pg_discuss import models

class AdminExt(ext.AppExtBase):
    def init_app(self, app):
        admin = flask_admin.Admin(app, 'Admin Models', template_mode='bootstrap3')
        # Add views
        admin.add_view(CommentAdmin(models.Comment, models.db.session))
        admin.add_view(ThreadAdmin(models.Thread, models.db.session))
        admin.add_view(IdentityAdmin(models.Identity, models.db.session))

class CommentAdmin(sqla.ModelView):
    pass

class ThreadAdmin(sqla.ModelView):
    pass

class IdentityAdmin(sqla.ModelView):
    pass
