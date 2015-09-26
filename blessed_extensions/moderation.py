import flask
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext, lazy_gettext
from flask_admin.base import expose
from flask_admin.contrib.sqla import filters
import sqlalchemy as sa

from . import admin
from pg_discuss import ext
from pg_discuss import models
from pg_discuss import tables
from pg_discuss.db import db

class Moderate(admin.PrettyComment):
    pass

class ModerationExt(ext.AppExtBase, ext.AddCommentFilterPredicate):

    def init_app(self, app):
        app.admin.add_view(CommentAdminWithModeration(
            Moderate,
            models.db.session,
            name='Moderation',
            endpoint='moderation',
        ))

    def add_comment_filter_predicate(self, **extras):
        """Return a filter clause to exclude unapproved comments from the
        default fetch.
        """
        t = tables.comment
        return t.c.custom_json['approved'].cast(sa.Boolean).is_(True)

class PendingApprovalFilter(filters.BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        t = tables.comment
        if value:
            return query.filter(t.c.custom_json['approved']==value)
        else:
            return query.filter(sa.not_(t.c.custom_json.has_key('approved')))
    def operation(self):
        return lazy_gettext('is')

class CommentAdminWithModeration(admin.CommentAdmin):

    column_list = ('identity', 'thread', 'text')
    can_delete = False
    can_create = False
    column_filters = [PendingApprovalFilter(
        models.Comment.custom_json,
        'Approval Status',
        [('', 'Pending'),
         ('true', 'Approved'),
         ('false', 'Rejected')])]

    @expose('/')
    def index_view(self):
        """Redirect to default 'Pending' filter if no query args."""
        if not flask.request.args:
            return flask.redirect(flask.request.url + '?flt1_0=')
        else:
            return super(CommentAdminWithModeration, self).index_view()

    @action('approve',
            lazy_gettext('Approve'),
            lazy_gettext('Are you sure you want to approve selected records?'))
    def action_approve(self, ids):
        self.set_approval(ids, 'approve')

    @action('reject',
            lazy_gettext('Reject'),
            lazy_gettext('Are you sure you want to reject selected records?'))
    def action_reject(self, ids):
        self.set_approval(ids, 'reject')

    def set_approval(self, ids, action):
        if action == 'approve':
            jsonb_val = 'true'
            action_text = 'approved'
        elif action == 'reject':
            jsonb_val = 'false'
            action_text = 'rejected'

        try:
            t = tables.comment
            approved = sa.func.jsonb_set(
                sa.text('custom_json'),
                sa.text("'{approved}'"),
                sa.text("'{}'::jsonb".format(jsonb_val))
            )
            stmt = (
                t.update()
                .where(t.c.id.in_(ids))
                .values(custom_json=approved)
                .returning(t.c.id)
            )
            result = db.engine.execute(stmt).fetchall()
            count = len(result)

            flask.flash(ngettext(
                'Comment was successfully {}.'
                .format(action_text),
                '%(count)s comments were successfully {}.'
                .format(action_text),
                count,
                count=count))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flask.flash(gettext('Failed to {} records. %(error)s'
                          .format(action_text),
                          error=str(ex)), 'error')
