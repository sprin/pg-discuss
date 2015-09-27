"""Queries used by pg-discuss core and available to extensions."""
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql

from . import ext
from . import tables
from . import utils
from .db import db


class CommentNotFoundError(Exception):
    pass


class ThreadNotFoundError(Exception):
    pass


class IdentityNotFoundError(Exception):
    pass


def fetch_thread_by_client_id(thread_client_id):
    """Fetch a thread object by thread_client_id from the database."""
    t = tables.thread
    stmt = t.select().where(t.c.client_id == thread_client_id)

    # TODO: Run on_pre_thread_fetch hooks
    # stmt = ext.exec_filter_hooks(ext.OnPreThreadFetch, stmt)

    result = db.engine.execute(stmt).first()
    if not result:
        raise ThreadNotFoundError(
            'Thread {0} not found'.format(thread_client_id)
        )
    comment = dict(result.items())

    return comment


def fetch_comment_by_id(comment_id):
    """Fetch a single comment object by id from the database."""
    t = tables.comment
    stmt = t.select().where(t.c.id == comment_id)

    # Run add_comment_filter_predicate hooks
    stmt = ext.exec_filter_hooks(ext.AddCommentFilterPredicate, stmt)

    result = db.engine.execute(stmt).first()
    if not result:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))
    comment = dict(result.items())

    return comment


def fetch_comments_by_thread_client_id(thread_client_id):
    """Fetch a list of comments for the given thread's client_id from the
    database."""
    t_comment = tables.comment
    t_thread = tables.thread
    stmt = (
        sa.select(t_comment.c)
        .select_from(sa.join(t_comment, t_thread))
        .where(t_thread.c.client_id == thread_client_id)
    )

    # Run add_comment_filter_predicate hooks
    stmt = ext.exec_filter_hooks(ext.AddCommentFilterPredicate, stmt)

    result = db.engine.execute(stmt)
    comments_seq = [dict(x) for x in result]

    return comments_seq


def insert_comment(new_comment):
    """Insert the `new_comment` object in to the database."""
    t = tables.comment
    stmt = (
        t.insert()
        .values(**new_comment)
        .returning(*list(t.c))
    )

    # Run on_pre_insert hooks
    ext.exec_hooks(ext.OnPreCommentInsert, new_comment)

    result = db.engine.execute(stmt).first()
    comment = dict(result.items())

    # Run on_post_insert hooks
    ext.exec_hooks(ext.OnPostCommentInsert, comment)

    return comment


def insert_thread(new_thread):
    """Insert the `new_thread` object in to the database."""
    t = tables.thread
    stmt = (
        t.insert()
        .values(**new_thread)
        .returning(*list(t.c))
    )

    # TODO: Run on_pre_thread_insert hooks
    # ext.exec_hooks(ext.OnPreThreadInsert, new_thread)

    result = db.engine.execute(stmt).first()
    thread = dict(result.items())

    # TODO: Run on_post_thread_insert hooks
    # ext.exec_hooks(ext.OnPostThreadInsert, thread)

    return thread


def insert_identity(new_identity=None):
    """Insert the a new identity object in to the database."""
    t = tables.identity
    stmt = (
        t.insert()
        .returning(*list(t.c))
    )
    if new_identity:
        stmt = stmt.values(**new_identity)

    # TODO: Run on_pre_identity_insert hooks
    # ext.exec_hooks(ext.OnPreIdentityInsert, new_identity)

    result = db.engine.execute(stmt).first()
    identity = dict(result.items())

    # TODO: Run on_post_identity_insert hooks
    # ext.exec_hooks(ext.OnPostIdentityInsert, identity)

    return identity


def update_identity(identity_id, identity_edit, old_identity):
    """Update the identity in the database.

    Update requests should be validated before being passed to this function.
    """
    t = tables.identity

    if 'custom_json' in identity_edit:
        identity_edit['custom_json'] = dict(
            old_identity['custom_json'],
            **identity_edit['custom_json']
        )

    # Update the "old" identity in place.
    stmt = (
        t.update()
        .where(t.c.id == identity_id)
        .values(**identity_edit)
        .returning(*list(t.c))
    )

    # Run on_pre_update hooks
    # ext.exec_hooks(ext.OnPreIdentityUpdate, old_identity, identity_edit)

    result = db.engine.execute(stmt).first()
    if not result:
        raise IdentityNotFoundError(
            'Identity {0} not found'.format(identity_id))

    identity = dict(result.items())

    # Run on_post_update hooks
    # ext.exec_hooks(ext.OnPostIdentityUpdate, old_identity, identity)

    return identity


def fetch_identity(identity_id):
    """Fetch an identity object by id from the database."""
    t = tables.identity
    stmt = t.select().where(t.c.id == identity_id)

    # TODO: Run on_pre_identity_fetch hooks
    # stmt = ext.exec_filter_hooks(ext.OnPreIdentityFetch, stmt)

    result = db.engine.execute(stmt).first()
    if not result:
        raise IdentityNotFoundError(
            'Identity {0} not found'.format(identity_id)
        )
    identity = dict(result.items())

    return identity


def update_comment(comment_id, comment_edit, old_comment,
                   update_modified=False):
    """Update the comment in the database in response to a request
    from the author. The `modified` timestamp will be set to the current time.

    Update requests should be validated before being passed to this function.
    """
    t = tables.comment

    if 'custom_json' in comment_edit:
        comment_edit['custom_json'] = dict(
            old_comment['custom_json'],
            **comment_edit['custom_json']
        )

    # Update the "old" comment in place.
    stmt = (
        t.update()
        .where(t.c.id == comment_id)
        .values(**comment_edit)
        .returning(*list(t.c))
    )

    # Update the `modified` timestamp if specified.
    if update_modified:
        stmt = stmt.values(modified=sa.text('NOW()'))

    # Run on_pre_update hooks
    ext.exec_hooks(ext.OnPreCommentUpdate, old_comment, comment_edit)

    result = db.engine.execute(stmt).first()
    if not result:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))

    comment = dict(result.items())

    # Run on_post_update hooks
    ext.exec_hooks(ext.OnPostCommentUpdate, old_comment, comment)

    return comment


def validate_parent_exists(parent):
    """Validate that the parent exists in the database."""
    t = tables.comment
    stmt = sa.select([sa.exists([1]).where(t.c.id == parent)])
    return db.engine.execute(stmt).scalar()


def insert_identity_comment(identity_comment):
    """Insert the a new identity-to-comment object in to the database."""
    t = tables.identity_comment
    stmt = (
        t.insert()
        .values(**identity_comment)
        .returning(*list(t.c))
    )
    result = db.engine.execute(stmt).first()
    identity_comment = dict(result.items())

    # TODO: Run on_post_identity_comment_insert hooks
    # ext.exec_hooks(ext.OnPostIdentityInsert, identity)

    return identity_comment


def cte_chain(statements):
    """Chain a sequence of statements using a CTE. The result of the last
    statement will be returned when RETURNING is used."""
    parts = []
    bindparams = {}
    for i, stmt in enumerate(statements):
        compiled = stmt.compile(
            dialect=sqlalchemy.dialects.postgresql.dialect())
        # If first statement, open the WITH statement and use an alias.
        if i == 0:
            part = "WITH t{0} AS ( {1} )".format(i, compiled)
        # If last statement, do not prefix with comma and do not use an alias.
        elif i == (len(statements) - 1):
            part = "{0}".format(compiled)
        # Otherwise, if not first or last, prefix with comma and use an alias.
        else:
            part = ", t{0} AS ( {1} )".format(i, compiled)

        bindparams = utils.merge_fail_on_conflict(bindparams, compiled.params)
        parts.append(part)

    stmt = '\n'.join(parts)
    return stmt, bindparams
