import flask
from voluptuous import (
    All,
    Schema,
    Url,
)

from pg_discuss import _compat
from pg_discuss import ext

class CaptureWebsite(ext.ValidateComment, ext.OnPreCommentSerialize):
    def validate_comment(self, comment, action, **extras):
        website = flask.request.get_json().get('website')
        if website:
            form = Schema(All(_compat.text_type, Url()))
            url = form(website)
            comment['custom_json']['website'] = normalize_url(url)
        return comment

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        if 'website' in raw_comment['custom_json']:
            client_comment['website'] = raw_comment['custom_json']['website']

def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url
