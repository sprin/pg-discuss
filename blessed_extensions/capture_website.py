from flask import request
from voluptuous import (
    All,
    Schema,
    Url,
)

from pg_discuss import ext

class CaptureWebsite(ext.ValidateComment, ext.OnCommentPreSerialize):
    def validate_comment(self, comment, **extras):
        website = request.get_json().get('website')
        if website:
            url = Schema(All(unicode, Url()))(website)
            comment['custom_json']['website'] = normalize_url(url)
        return comment

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        if 'website' in raw_comment['custom_json']:
            client_comment['website'] = raw_comment['custom_json']['website']

def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url
