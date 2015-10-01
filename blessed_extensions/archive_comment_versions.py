import sqlalchemy as sa

from pg_discuss import ext
from pg_discuss import tables
from pg_discuss.db import db


class ArchiveCommentVersionsExt(ext.OnPostCommentUpdate,
                                ext.AddCommentFilterPredicate):
    """Extension to archive comment versions.

    When a comment has been edited through the HTTP API, a version is saved
    as another Comment record. Old versions always have a foreign key to the
    most recent version of the comment in `version_of_id`.
    """

    def on_post_comment_update(self, old_comment, new_comment, **extras):
        # "Archive" the old version of the comment by re-inserting it, with a
        # new pk.  Set `archived` to True.
        t = tables.comment
        old_comment['version_of_id'] = old_comment['id']
        del old_comment['id']
        old_comment['custom_json']['archived'] = True
        stmt = (
            t.insert()
            .values(**old_comment)
        )
        db.engine.execute(stmt)

    def add_comment_filter_predicate(self, **extras):
        """Return a filter clause to exclude archived comments from the default
        fetch.
        """
        t = tables.comment
        return t.c.custom_json['archived'].cast(sa.Boolean).isnot(True)
