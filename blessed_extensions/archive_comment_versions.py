import sqlalchemy as sa

from pg_discuss import db
from pg_discuss import ext
from pg_discuss import tables

class ArchiveCommentVersionsExt(ext.OnPostCommentUpdate,
                                ext.AddCommentFilterPredicate):

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