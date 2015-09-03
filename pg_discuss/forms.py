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

def exec_comment_validators(action):
    """Validate comment with all configured validators.

    Validation Exceptions raised within validator functions will be propagated
    up and processing will be stopped.

    If no validator raises an Exception, the result of the last validator
    will be returned.

    The `action` string is supplied to each extension. Possible actions are:
    'new', 'edit'.
    """

    def validator(comment):
        result = ext.exec_hooks(ext.ValidateComment, comment, action)
        if len(result) > 0:
            return result[-1]
    return validator

def validate_new_comment(new_comment):
    new_comment_schema = All(
        Schema({
            'parent_id': All(Any(int, None), validate_parent),
            Required('text'): unicode,
            Required('custom_json'): dict,
            Required('identity_id'): Any(int, None),
        }),
        exec_comment_validators(action='new'),
    )

    return new_comment_schema(new_comment)

def validate_comment_edit(comment_edit):
    """Validate a commment edit. This differs from validating a new comment in
    that `parent_id` is not allowed to be included - the parent cannot be
    changed by editing.
    """
    comment_edit_schema = All(
        Schema({
            Required('text'): unicode,
            Required('custom_json'): dict,
        }),
        exec_comment_validators(action='edit'),
    )

    return comment_edit_schema(comment_edit)
