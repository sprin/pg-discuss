from flask import jsonify

from pg_discuss import ext
from pg_discuss import tables
from pg_discuss.models import db

import sqlalchemy as sa

class Voting(ext.AppExtBase, ext.OnPreCommentSerialize):

    def init_app(self, app):
        app.route('/comments/<int:comment_id>/upvote', methods=['POST'])(self.upvote)
        app.route('/comments/<int:comment_id>/downvote', methods=['POST'])(self.downvote)

    def upvote(self, comment_id):
        return self.vote(comment_id, keyname='upvotes')

    def downvote(self, comment_id):
        return self.vote(comment_id, keyname='downvotes')

    def vote(self, comment_id, keyname):
        """Add a new vote and increase the upvotes counter.

        Note: Use`jsonb_set` function in 9.5 to do an in-place increment:

            update comment
            set custom_json = jsonb_set(
                custom_json,
                '{upvotes}',
                coalesce(
                ((custom_json->>'upvotes')::integer + 1)::text::jsonb,
                '1')
            )
            where id = %id;
        """

        t = tables.comment
        incremented = sa.func.jsonb_set(
            sa.text('custom_json'),
            sa.text("'{{{0}}}'".format(keyname)),
            sa.text(
                "coalesce(((custom_json->>'{0}')::integer + 1)::text::jsonb,'1')"
                .format(keyname)
            )
        )
        stmt = (
            t.update()
            .where(t.c.id == comment_id)
            .values(custom_json=incremented)
            .returning(t.c.custom_json['upvotes'], t.c.custom_json['downvotes'])
        )
        results = db.engine.execute(stmt).first()
        resp_obj = {
            'upvotes': results[0],
            'downvotes': results[1]
        }
        return jsonify(resp_obj)

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        client_comment['upvotes'] = raw_comment['custom_json'].get('upvotes', 0)
        client_comment['downvotes'] = raw_comment['custom_json'].get('downvotes', 0)
