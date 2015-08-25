from pg_discuss import ext
from pg_discuss.models import db
from pg_discuss import tables

class ArchiveUpdatesExt(ext.DoOnUpdateMixin):

    def do_on_update(self, old_comment, new_comment):
        # "Archive" the old comment by re-inserting it, with a new pk.
        # Set `active` to False.
        t = tables.comment
        old_comment['archived_from'] = old_comment['id']
        del old_comment['id']
        old_comment['active'] = False
        stmt = (
            t.insert()
            .values(**old_comment)
        )
        db.engine.execute(stmt)
