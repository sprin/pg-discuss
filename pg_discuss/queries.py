from . import tables
from .models import db

from sqlalchemy.sql import (
    select,
    exists,
)

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

    # Set `text` to None if marked deleted.
    if comment['deleted']:
        comment['text'] = None

    return comment

def insert_comment(new_comment):
    """Insert the `new_comment` object in to the database."""
    t = tables.comment
    stmt = (
        t.insert()
        .values(**new_comment)
        .returning(*list(t.c))
    )

    # TODO: Pass stmt, new_comment, and req to extensions iterator
    result = db.engine.execute(stmt)
    return dict(result.first().items())

def update_comment(comment_id, comment_edit):
    """Update the comment in to the database."""
    t = tables.comment
    stmt = (
        t.update()
        .where(t.c.id == comment_id)
        .values(**comment_edit)
        .returning(*list(t.c))
    )

    # TODO: Pass stmt, new_comment, and req to extensions iterator
    result = db.engine.execute(stmt)
    comment = result.first()
    if not comment:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))
    return dict(comment.items())

def validate_parent_exists(parent):
    """Validate that the parent exists in the database."""
    t = tables.comment
    stmt = select([exists([1]).where(t.c.id == parent)])
    return db.engine.execute(stmt).scalar()
