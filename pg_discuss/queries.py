from . import tables
from .models import db

from sqlalchemy.sql import (
    select,
    exists,
    text,
)
from . import ext

class CommentNotFoundError(Exception):
    pass

def fetch_comment(comment_id):
    """Fetch a comment by id from the database."""
    t = tables.comment
    stmt = t.select().where(t.c.id == comment_id)
    result = db.engine.execute(stmt).first()
    if not result:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))
    comment = dict(result.items())

    return comment

def insert_comment(new_comment):
    """Insert the `new_comment` object in to the database."""
    t = tables.comment
    stmt = (
        t.insert()
        .values(**new_comment)
        .returning(*list(t.c))
    )

    # Run on_pre_insert hooks
    ext.exec_hooks(ext.OnPreInsert, new_comment, stmt)

    result = db.engine.execute(stmt).first()
    comment = dict(result.items())

    # Run on_post_insert hooks
    ext.exec_hooks(ext.OnPostInsert, comment)

    return comment

def update_comment(comment_id, comment_edit, update_modified=False):
    """Update the comment in the database in response to a request
    from the author. The `modified` timestamp will be set to the current time.

    Update requests should be validated before being passed to this function.
    """
    t = tables.comment
    # Fetch the "old" comment
    old_comment = fetch_comment(comment_id)

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
    ext.exec_hooks(ext.OnPreUpdate, old_comment, comment_edit, stmt)

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
