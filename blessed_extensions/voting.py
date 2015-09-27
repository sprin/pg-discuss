import flask

from pg_discuss import ext
from pg_discuss import queries
from pg_discuss import tables
from pg_discuss.db import db

import sqlalchemy as sa

class Voting(ext.AppExtBase, ext.OnPreCommentSerialize):

    def init_app(self, app):
        app.route('/comments/<int:comment_id>/upvote', methods=['POST'])(self.upvote)
        app.route('/comments/<int:comment_id>/downvote', methods=['POST'])(self.downvote)

    def upvote(self, comment_id):
        return self.vote(comment_id, vote_type='upvote')

    def downvote(self, comment_id):
        return self.vote(comment_id, vote_type='downvote')

    def vote(self, comment_id, vote_type):
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

        identity_comment = {
            'identity_id': flask.g.identity['id'],
            'comment_id': comment_id,
            'rel_type': vote_type,
        }
        t = tables.identity_comment
        ins = (
            t.insert()
            .values(**identity_comment)
            .returning(*list(t.c))
        )
        keyname = "{0}s".format(vote_type) # add 's' to pluralize vote_type
        t = tables.comment
        incremented = sa.func.jsonb_set(
            sa.text('custom_json'),
            sa.text("'{{{0}}}'".format(keyname)),
            sa.text(
                "coalesce(((custom_json->>'{0}')::integer + 1)::text::jsonb,'1')"
                .format(keyname)
            )
        )
        upd = (
            t.update()
            .where(t.c.id == comment_id)
            .values(custom_json=incremented)
            .returning(t.c.custom_json['upvotes'], t.c.custom_json['downvotes'])
        )
        statements = [ins, upd]
        stmt, bindparams = queries.cte_chain(statements)
        try:
            results = db.engine.execute(stmt, **bindparams).first()
        except sa.exc.IntegrityError:
            flask.abort(400,
                  'Cannot {0} on comment: identity has already submitted {0}'
                  .format(vote_type)
                 )


        resp_obj = {
            'upvotes': results[0],
            'downvotes': results[1]
        }
        return flask.jsonify(resp_obj)

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        client_comment['upvotes'] = raw_comment['custom_json'].get('upvotes', 0)
        client_comment['downvotes'] = raw_comment['custom_json'].get('downvotes', 0)
