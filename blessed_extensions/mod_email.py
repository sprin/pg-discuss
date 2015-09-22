import os
import flask
import flask_mail
from pg_discuss import ext

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
        msg = flask_mail.Message(subject=subject, body=body,
                            recipients=["steffen@sprin.io"])
        self.mail.send(msg)
