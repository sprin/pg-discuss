from flask import request
from voluptuous import (
    All,
    Schema,
    Url,
)

from pg_discuss import ext
from pg_discuss import _compat

class CaptureWebsite(ext.ValidateComment, ext.OnPreCommentSerialize):
    def validate_comment(self, comment, action, **extras):
        website = request.get_json().get('website')
        if website:
            url = Schema(All(_compat.text_type, Url()))(website)
            comment['custom_json']['website'] = normalize_url(url)
        return comment

    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        if 'website' in raw_comment['custom_json']:
            client_comment['website'] = raw_comment['custom_json']['website']

def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url
