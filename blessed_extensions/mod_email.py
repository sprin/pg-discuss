"""Send a mail to the administrators when new comments are submitted.

Include a link to the Admin panel.
"""
import os
from threading import Thread

import flask
import flask_mail
import sqlalchemy as sa

from pg_discuss import tables
from pg_discuss import ext
from pg_discuss.db import db


class ModerationEmail(ext.AppExtBase, ext.OnPostCommentInsert):

    mail_settings_from_env = [
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_USE_SSL',
        'MAIL_USE_TLS',
    ]

    def init_app(self, app):
        self.get_settings_from_env(app)
        self.mail = flask_mail.Mail(app)
        app.config.setdefault('MAIL_SEND_ASYNC', True)

    def get_settings_from_env(self, app):
        for setting in self.mail_settings_from_env:
            val = os.environ.get(setting)
            if val:
                if setting in ['MAIL_USE_TLS', 'MAIL_USE_SSL']:
                    app.config[setting] = (val == 'True')
                else:
                    app.config[setting] = val

    def on_post_comment_insert(self, comment):
        subject = "pg-discuss: New comment from {}".format(
            comment['custom_json']['author'])
        body = (
            "Moderation panel:\n{url}\n\n{author} posted:\n\n{comment}"
            .format(
                url=flask.url_for('moderation.index_view', _external=True),
                author=comment['custom_json']['author'],
                comment=comment['text']
            ))
        msg = flask_mail.Message(subject=subject, body=body)
        # Send asynchronously in a thread, if enabled.
        if self.app.config['MAIL_SEND_ASYNC']:
            thr = Thread(target=send_async_email,
                         args=[self.app, msg, self.mail])
            thr.start()
        else:
            recipients = fetch_admin_emails()
            for recipient in recipients:
                msg.add_recipient(recipient)
            self.mail.send(msg)


def fetch_admin_emails():
    stmt = sa.select([tables.admin_user.c.email])
    result = db.engine.execute(stmt).fetchall()
    if result:
        return [x[0] for x in list(result)]


def send_async_email(app, msg, mail):
    with app.app_context():
        recipients = fetch_admin_emails(app)
        for recipient in recipients:
            msg.add_recipient(recipient)
        mail.send(msg)
