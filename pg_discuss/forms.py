from flask import current_app
from voluptuous import (
    Schema,
    Required,
    All,
    Length,
    Invalid,
)
from pg_discuss.queries import validate_parent_exists

def validate_parent(parent):
    if not validate_parent_exists(parent):
        raise Invalid('parent does not exist')
    return parent

def validate_new_comment(
    new_comment,
    min_comment_length=None,
    max_comment_length=None
):
    if not min_comment_length:
        min_comment_length = current_app.config['MIN_COMMENT_LENGTH']

    if not max_comment_length:
        max_comment_length = current_app.config['MAX_COMMENT_LENGTH']

    new_comment_schema = Schema({
            'parent': All(int, validate_parent),
            Required('text'): All(
                unicode,
                Length(min=min_comment_length, max=max_comment_length)
            ),
    })

    return new_comment_schema(new_comment)

