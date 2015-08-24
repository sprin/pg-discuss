from flask import current_app
from voluptuous import (
    Schema,
    Required,
    All,
    Length,
    Invalid,
)
from .queries import validate_parent_exists

def validate_parent(parent):
    if not validate_parent_exists(parent):
        raise Invalid('parent does not exist')
    return parent

def default_comment_text_validator_factory(
    min_comment_length=None,
    max_comment_length=None,
):
    if not min_comment_length:
        min_comment_length = current_app.config['MIN_COMMENT_LENGTH']

    if not max_comment_length:
        max_comment_length = current_app.config['MAX_COMMENT_LENGTH']

    return All(
        unicode,
        Length(min=min_comment_length, max=max_comment_length)
    )

def validate_new_comment(
    new_comment,
    min_comment_length=None,
    max_comment_length=None,
):
    new_comment_schema = Schema({
            'parent': All(int, validate_parent),
            Required('text'): comment_text_validator(
                min_comment_length,
                max_comment_length,
            )
    })

    return new_comment_schema(new_comment)

