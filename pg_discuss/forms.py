from voluptuous import (
    Schema,
    Required,
    All,
    Any,
    Invalid,
)
from .queries import validate_parent_exists
from . import ext

def validate_parent(parent):
    if parent is not None and not validate_parent_exists(parent):
        raise Invalid('parent does not exist')
    return parent

def exec_comment_validators(comment):
    """Validate comment with all configured validators.

    Validation Exceptions raised within validator functions will be propagated
    up and processing will be stopped.

    If no validator raises an Exception, the result of the last validator
    will be returned.
    """

    result = ext.exec_hooks(ext.ValidateComment, comment)
    if len(result) > 0:
        return result[-1]

def validate_new_comment(
    new_comment,
    min_comment_length=None,
    max_comment_length=None,
):
    new_comment_schema = All(
        Schema({
            'parent': All(Any(int, None), validate_parent),
            Required('text'): All(unicode)
        }),
        exec_comment_validators,
    )

    return new_comment_schema(new_comment)
