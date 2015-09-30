import os
from threading import Thread

import flask
import flask_mail
import sqlalchemy as sa

from pg_discuss import tables
from pg_discuss import ext
from pg_discuss.db import db

#: Host to use for sending email.
MAIL_HOST = None
#: Port to use for sending email.
MAIL_PORT = None
#: Username to use to authenticate with the SMTP server.
MAIL_USERNAME = None
#: Password to use to authenticate with the SMTP server.
MAIL_PASSWORD = None
#: Use an explicit secure connection using TLS/SSL negotiation.
#: Typically uses port 465.
#:
#: Internally, this setting is translated to Flask-Mail's `MAIL_USE_SSL`
#: setting.
MAIL_SECURE_CONNECTION = True
#: Use STARTTLS. This is a broken protocol, trivially exploitable by MitM.
#: Use an explicit TLS connection instead if possible.
#: See: https://www.agwa.name/blog/post/starttls_considered_harmful
#:
#: Typically uses port 587.
#:
#: `MAIL_SECURE_CONNECTION` and `MAIL_USE_STARTTLS` are mutually exclusive,
#: and an error will be raised if both are set to True.
#:
#: Internally, this setting is translated to Flask-Mail's `MAIL_USE_TLS`
#: setting.
MAIL_USE_STARTTLS = False
#: Send mail asynchronously by spawning a thread. Dramatically improves
#: response times for posting new comments.
MAIL_SEND_ASYNC = True


class ModerationEmail(ext.AppExtBase, ext.OnPostCommentInsert):
    """Extensions to send a mail to the administrators when new comments are
    submitted. All registered administrators will receive a mail.

    Include a link to the Admin panel.
    """

    mail_settings_from_env = [
        'MAIL_HOST',
        'MAIL_PORT',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_SECURE_CONNECTION',
        'MAIL_USE_STARTTLS',
    ]

    def init_app(self, app):
        app.config.setdefault('MAIL_HOST', MAIL_HOST)
        app.config.setdefault('MAIL_PORT', MAIL_PORT)
        app.config.setdefault('MAIL_USERNAME', MAIL_USERNAME)
        app.config.setdefault('MAIL_PASSWORD', MAIL_PASSWORD)
        app.config.setdefault('MAIL_SECURE_CONNECTION', MAIL_SECURE_CONNECTION)
        app.config.setdefault('MAIL_USE_STARTTLS', MAIL_USE_STARTTLS)
        app.config.setdefault('MAIL_SEND_ASYNC', MAIL_SEND_ASYNC)

        # Get email connection settings from environment, by default.
        self.get_settings_from_env(app)
        if (
            app.config['MAIL_SECURE_CONNECTION']
            and app.config['MAIL_USE_STARTTLS']
        ):
            raise Exception(
                'Only one of MAIL_SECURE_CONNECTION and MAIL_USE_STARTTLS '
                'may be True')
        # Translate MAIL_SECURE_CONNECTION to Flask-Mail's MAIL_USE_SSL
        app.config['MAIL_USE_SSL'] = app.config['MAIL_SECURE_CONNECTION']
        # Translate MAIL_USE_STARTTLS to Flask-Mail's MAIL_USE_TLS
        app.config['MAIL_USE_TLS'] = app.config['MAIL_USE_STARTTLS']

        self.mail = flask_mail.Mail(app)

    def get_settings_from_env(self, app):
        for setting in self.mail_settings_from_env:
            val = os.environ.get(setting)
            if val:
                if setting in ['MAIL_SECURE_CONNECTION', 'MAIL_USE_STARTTLS']:
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
