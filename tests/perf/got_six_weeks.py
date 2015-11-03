"""Time fetching a very large comment thread. As a data source, fetches the
longest-running reddit thread of 33K comments via the reddit API, which will
likely take several hours due to being limited to 200 comments per request and
API rate limits.
https://www.reddit.com/r/science/comments/6nz1k/got_six_weeks_try_the_hundred_push_ups_training/

This is not meant to be run as part of the normal regression suite since we
cannot fetch the file every time, nor can we store it in the repository.

`fetch_got_six_weeks_from_reddit` fetches the thread and dumps it to a JSON
file (30MB). Uses the `PRAW`_ reddit API client to handle recursively fetching
the comments.

.. _`PRAW`: https://praw.readthedocs.org/en/latest/index.html

`load_got_six_weeks` will load all comments from the JSON file in to the
database

`time_got_six_weeks_fetch` will time how long the pg-discuss fetch API
takes to produce the entire thread. This is useful in conjunction with the
:mod:`blessed_extensions.profiler` extension to examine performance
bottlenecks.
"""

import argparse
import datetime
import json
import sqlalchemy as sa
import timeit

from pg_discuss import tables
from pg_discuss.app import app_factory
from pg_discuss.db import db
from blessed_extensions.isso_client_shim import hash


def fetch_got_six_weeks_from_reddit():
    import praw

    r = praw.Reddit('PRAW comment scraper')
    r.config.store_json_result = True

    submission = r.get_submission(submission_id='6nz1k')
    submission.replace_more_comments(limit=None, threshold=0)
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    comments_json = [dict(c.json_dict) for c in flat_comments]
    for c in comments_json:
        c['replies'] = None
    print(json.dumps(comments_json))


def load_got_six_weeks():
    app = app_factory()
    thread_cid = 'got_six_weeks'
    thread_id = 1
    to_insert = []

    # First, change comment.id to a bigint to handle reddit's 36-bit
    # ids. Note this will succeed even when the column is already a bigint.
    with app.app_context():
        db.engine.execute(sa.text('''
    ALTER TABLE comment ALTER COLUMN id TYPE bigint
        '''))
        db.engine.execute(sa.text('''
    ALTER TABLE comment ALTER COLUMN parent_id TYPE bigint
        '''))
        db.engine.execute(sa.text('''
    ALTER TABLE identity_comment ALTER COLUMN comment_id TYPE bigint
        '''))

        with open('got_six_weeks.json') as f:
            comments = json.loads(f.read())

            submission_id = None
            for i, c in enumerate(comments):
                id = int(c['id'], 36)
                text = c['body']
                created = datetime.datetime.fromtimestamp(c['created'])
                custom_json = {
                    'author': c['author'],
                }
                if c['author'] != '[deleted]':
                    custom_json['hash'] = hash(c['author'])
                comment_to_insert = {
                    'id': id,
                    'thread_id': thread_id,
                    'text': text,
                    'created': created,
                    'custom_json': custom_json,
                }
                # Ignore parent_id for comments which reply to the submission.
                # The first comment is a reply to the submission, so we
                # can track the submission id that way.
                if i == 0:
                    submission_id = c['parent_id']
                    comment_to_insert['parent_id'] = None
                elif c['parent_id'] == submission_id:
                    comment_to_insert['parent_id'] = None
                else:
                    parent_id = int(c['parent_id'][3:], 36)
                    comment_to_insert['parent_id'] = parent_id

                to_insert.append(comment_to_insert)

        db.engine.execute(
            tables.thread.insert(),
            **{
                'id': 1,
                'client_id': thread_cid,
            })

        db.engine.execute(
            tables.comment.insert(),
            to_insert,
        )


def time_got_six_weeks_fetch():
    setup = (
        "from pg_discuss.app import app_factory;"
        "app = app_factory();"
        "client = app.test_client()"
    )
    return timeit.timeit(
        "client.get('/threads/got_six_weeks/comments')",
        setup=setup,
        number=1
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage=(
        "got_six_weeks.py performance test. See module docstring.\n\n"
        "got_six_weeks.py [fetch | load | time]"
    ))
    parser.add_argument("action")
    args = parser.parse_args()

    if args.action == 'fetch':
        print('fetching from reddit (this may take several hours')
        fetch_got_six_weeks_from_reddit()
    elif args.action == 'load':
        print('loading comments in to database')
        load_got_six_weeks()
    elif args.action == 'time':
        print('timing fetch api')
        print('Took: {}'.format(time_got_six_weeks_fetch()))
    else:
        print("unknown action {}. use one of: [fetch | load | time]"
              .format(args.action))
