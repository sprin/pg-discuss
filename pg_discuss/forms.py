"""
Forms to validate new comments and comment edits. These forms will execute
any hooks associated with `ValidateComment` extensions.
"""
from voluptuous import (
    Schema,
    Required,
    All,
    Any,
    Invalid,
)

from . import _compat
from . import ext
from . import queries

def validate_parent(parent_id):
    """Validate that the parent_id associated with a new comment corresponds to
    a valid parent comment.
    """
    if parent_id is not None and not queries.validate_parent_exists(parent_id):
        raise Invalid('parent does not exist')
    return parent_id

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
        """Validate the comment against all configured ValidateComment
        extensions.
        """
        result = ext.exec_hooks(ext.ValidateComment, comment, action)
        if len(result) > 0:
            return result[-1]
    return validator

def validate_new_comment(new_comment):
    """Validate a new comment."""
    new_comment_schema = All(
        Schema({
            'parent_id': All(Any(int, None), validate_parent),
            Required('text'): _compat.text_type,
            Required('custom_json'): dict,
            Required('identity_id'): Any(int, None),
        }),
        exec_comment_validators(action='new'),
    )

    return new_comment_schema(new_comment)

def validate_comment_edit(comment_edit):
    """Validate a commment edit. This differs from validating a new comment in
    that `parent_id` is not allowed to be included - the parent cannot be
    changed by editing. Also, the `identity_id` may not be changed.
    """
    comment_edit_schema = All(
        Schema({
            Required('text'): _compat.text_type,
            Required('custom_json'): dict,
        }),
        exec_comment_validators(action='edit'),
    )

    return comment_edit_schema(comment_edit)
