from . import tables
from .models import db

from sqlalchemy.sql import (
    select,
    exists,
    text,
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
    # Fetch the "old" comment
    old_comment = fetch_comment(comment_id)
    # Update the "old" comment in place, setting `modified` to `NOW()`
    stmt = (
        t.update()
        .where(t.c.id == comment_id)
        .values(modified=text('NOW()'), **comment_edit)
        .returning(*list(t.c))
    )
    # TODO: Pass stmt, new_comment, and req to extensions iterator
    result = db.engine.execute(stmt)
    comment = result.first()
    if not comment:
        raise CommentNotFoundError('Comment {0} not found'.format(comment_id))

    # "Archive" the old comment by re-inserting it, with a new pk.
    # Set `active` to False.
    old_comment['archived_from'] = old_comment['id']
    del old_comment['id']
    old_comment['active'] = False
    stmt = (
        t.insert()
        .values(**old_comment)
    )
    db.engine.execute(stmt)

    return dict(comment.items())

def validate_parent_exists(parent):
    """Validate that the parent exists in the database."""
    t = tables.comment
    stmt = select([exists([1]).where(t.c.id == parent)])
    return db.engine.execute(stmt).scalar()
