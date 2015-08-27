from flask import (
    jsonify,
    request,
    current_app,
)
from voluptuous import (
    Schema,
    Required,
)

from pg_discuss.ext import AppExtBase
from pg_discuss import queries

class EditViewExt(AppExtBase):
    def init_app(self, app):
        app.route('/comments/<int:comment_id>', methods=['PATCH'])(edit)

def edit(comment_id):
    json = request.get_json()
    allowed_keys = ['text']
    comment_edit = {k: json[k] for k in allowed_keys if json.has_key(k)}

    # Validate required, type, text length
    # Use the id given in the URL path, ignoring any in the request JSON
    comment_edit = validate_comment_edit(comment_edit)

    # Update the comment
    result = queries.update_comment(
        comment_id,
        comment_edit,
        update_modified=True
    )
    return jsonify(result)

def validate_comment_edit(comment_edit):
    comment_edit_schema = Schema({
            Required('text'): current_app.comment_text_validator_factory()
    })

    return comment_edit_schema(comment_edit)
