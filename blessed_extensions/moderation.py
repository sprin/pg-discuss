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

#: Enable moderation by setting new posts to `pending`.
MODERATION_ACTIVE = True


class Moderate(admin.PrettyComment):
    pass


class ModerationExt(ext.AppExtBase, ext.AddCommentFilterPredicate,
    ext.OnPreCommentInsert):
    """Extension that requires comments to be approved by an admin user
    through the admin interface before publishing. Once this plugin is enabled,
    it can be deactivated by setting `MODERATION_ACTIVE` to False.
    Removing the plugin entirely will cause pending/rejected comments to
    appear, thus is not recommended unless some cleanup is done in the
    database.
    """
    def __init__(self, app):
        app.config.setdefault('MODERATION_ACTIVE', MODERATION_ACTIVE)

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
        return sa.or_(
            t.c.custom_json['mod_mode'].cast(sa.Text) == 'pending',
            t.c.custom_json['mod_mode'].cast(sa.Text) == 'rejected',
        )

    def on_pre_comment_insert(self, new_comment, **extras):
        """Set `mod_mode` to `pending`, unless `MODERATION_ACTIVE` is False.
        """
        if self.app.config['MODERATION_ACTIVE']:
            new_comment['custom_json']['mod_mode'] = 'pending'


class PendingApprovalFilter(filters.BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        t = tables.comment
        return query.filter(t.c.custom_json['mod_mode'].cast(sa.Text) == value)

    def operation(self):
        return lazy_gettext('is')


class CommentAdminWithModeration(admin.AuthenticatedModelView):

    column_list = ('identity', 'thread', 'text')
    can_delete = False
    can_create = False
    column_filters = [PendingApprovalFilter(
        models.Comment.custom_json,
        'Approval Status',
        [('pending', 'Pending'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')])]

    @expose('/')
    def index_view(self):
        """Redirect to default 'Pending' filter if no query args."""
        if not flask.request.args:
            return flask.redirect(flask.request.url + '?flt1_0=pending')
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
            jsonb_val = 'approved'
            action_text = 'approved'
        elif action == 'reject':
            jsonb_val = 'rejected'
            action_text = 'rejected'

        try:
            t = tables.comment
            mod_mode = sa.func.jsonb_set(
                sa.text('custom_json'),
                sa.text("'{mod_mode}'"),
                sa.text('\'"{}"\''.format(jsonb_val))
            )
            stmt = (
                t.update()
                .where(t.c.id.in_(ids))
                .values(custom_json=mod_mode)
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
