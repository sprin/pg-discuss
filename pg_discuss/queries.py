from pg_discuss import tables
from pg_discuss.models import db

from sqlalchemy.sql import (
    select,
    exists,
)

def validate_parent_exists(parent):
    """Validate that the parent exists in the database."""
    t = tables.comment
    stmt = select([exists([1]).where(t.c.id == parent)])
    return db.engine.execute(stmt).scalar()

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


