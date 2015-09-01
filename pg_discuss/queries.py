from . import tables
from .models import db

from sqlalchemy.sql import (
    select,
    exists,
    text,
    join,
)
from . import ext

class CommentNotFoundError(Exception):
    pass

class ThreadNotFoundError(Exception):
    pass

def fetch_thread_by_client_id(thread_client_id):
    t = tables.thread
    stmt = t.select().where(t.c.client_id == thread_client_id)

    # TODO: Run on_thread_pre_fetch hooks
    #stmt = ext.exec_query_hooks(ext.OnThreadPreFetch, stmt)

    result = db.engine.execute(stmt).first()
    if not result:
        raise ThreadNotFoundError(
            'Thread {0} not found'.format(thread_client_id)
        )
    comment = dict(result.items())

    return comment


def fetch_comment_by_id(comment_id):
    """Fetch a single comment by id from the database."""
    t = tables.comment
    stmt = t.select().where(t.c.id == comment_id)

    # Run on_pre_fetch hooks
    stmt = ext.exec_query_hooks(ext.OnPreFetch, stmt)

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
        select(t_comment.c)
        .select_from(join(t_comment, t_thread))
        .where(t_thread.c.client_id == thread_client_id)
    )

    # Run on_pre_fetch hooks
    stmt = ext.exec_query_hooks(ext.OnPreFetch, stmt)

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
    stmt = ext.exec_query_hooks(ext.OnPreInsert, stmt, new_comment)

    result = db.engine.execute(stmt).first()
    comment = dict(result.items())

    # Run on_post_insert hooks
    ext.exec_hooks(ext.OnPostInsert, comment)

    return comment

def insert_thread(new_thread):
    """Insert the `new_thread` object in to the database."""
    t = tables.thread
    stmt = (
        t.insert()
        .values(**new_thread)
        .returning(*list(t.c))
    )

    # TODO: Run on_pre_insert hooks
    #stmt = ext.exec_query_hooks(ext.OnThreadPreInsert, stmt, new_thread)

    result = db.engine.execute(stmt).first()
    thread = dict(result.items())

    # TODO: Run on_post_insert hooks
    #ext.exec_hooks(ext.OnPostInsert, comment)

    return thread

def update_comment(comment_id, comment_edit, update_modified=False):
    """Update the comment in the database in response to a request
    from the author. The `modified` timestamp will be set to the current time.

    Update requests should be validated before being passed to this function.
    """
    t = tables.comment
    # Fetch the "old" comment
    old_comment = fetch_comment_by_id(comment_id)

    if 'custom_json_patch' in comment_edit:
        comment_edit['custom_json'] = dict(
            old_comment['custom_json'],
            **comment_edit['custom_json_patch']
        )
        del comment_edit['custom_json_patch']

    # Update the "old" comment in place.
    stmt = (
        t.update()
        .where(t.c.id == comment_id)
        .values(**comment_edit)
        .returning(*list(t.c))
    )

    # Update the `modified` timestamp if specified.
    if update_modified:
        stmt = stmt.values(modified=text('NOW()'))

    # Run on_pre_update hooks
    stmt = ext.exec_query_hooks(
        ext.OnPreUpdate,
        stmt,
        old_comment,
        comment_edit,
    )

    result = db.engine.execute(stmt).first()
    if not result:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))

    comment = dict(result.items())

    # Run on_post_update hooks
    ext.exec_hooks(ext.OnPostUpdate, old_comment, comment)

    return comment

def validate_parent_exists(parent):
    """Validate that the parent exists in the database."""
    t = tables.comment
    stmt = select([exists([1]).where(t.c.id == parent)])
    return db.engine.execute(stmt).scalar()
