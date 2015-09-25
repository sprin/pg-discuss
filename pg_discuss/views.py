"""Minimal comment CRUD views.

 - fetch: fetch the list of comments for a thread
 - new: create a new comment
 - view: fetch a single comment
 - edit: update an existing comment
 - delete: delete a comment
"""
import flask
import flask_login

from . import queries
from . import forms
from . import serialize
from . import ext
from . import auth_forms

def fetch(thread_cid):
    """View to fetch the thread and it's comment collection as JSON."""
    raw_thread = queries.fetch_thread_by_client_id(thread_cid)
    comments_seq = queries.fetch_comments_by_thread_client_id(thread_cid)
    comments_seq = [serialize.to_client_comment(c) for c in comments_seq]
    client_thread = serialize.to_client_thread(raw_thread, comments_seq)
    return flask.jsonify(client_thread)

def new(thread_cid):
    """View to create a new thread."""
    # Extract whitelisted attributes from request JSON
    # Note that extensions have the opportunity to process/persist additional
    # attributes from the request JSON, since they have access to the
    # request and `new_comment` object
    json = flask.request.get_json()
    allowed_keys = ['parent_id', 'text']
    new_comment = {k: json[k] for k in allowed_keys if k in json}

    # Create empty `custom_json`, for extensions to populate.
    new_comment['custom_json'] = {}

    # Associate comment with identity
    new_comment['identity_id'] = flask.g.identity['id']

    # Validate required, type, text length
    new_comment = forms.validate_new_comment(new_comment)

    # Try to fetch the existing thread record
    try:
        thread = queries.fetch_thread_by_client_id(thread_cid)
    except queries.ThreadNotFoundError:
        # Create a new thread record if one does not exist.
        thread = queries.insert_thread({'client_id': thread_cid})

    new_comment['thread_id'] = thread['id']

    # Insert the comment
    raw_comment = queries.insert_comment(new_comment)
    client_comment = serialize.to_client_comment(raw_comment)

    resp = flask.jsonify(client_comment)
    resp.status_code = 201

    ext.exec_hooks(ext.OnNewCommentResponse, resp, raw_comment, client_comment)

    return resp

def view(comment_id):
    """View to fetch a single comment."""
    # Fetch the comment
    raw_comment = queries.fetch_comment_by_id(comment_id)

    # Check if client has request plain (not marked-up) text
    plain = flask.request.args.get('plain') == '1'

    comment = serialize.to_client_comment(raw_comment, plain)
    return flask.jsonify(comment)

def edit(comment_id):
    """View to edit an existing comment."""
    json = flask.request.get_json()
    comment_edit = {'text': json['text']}

    # Create empty `custom_json`, for extensions to populate.
    # This will later be merged in to the existing `custom_json`.
    comment_edit['custom_json'] = {}

    # Validate required, type, text length
    # Use the id given in the URL path, ignoring any in the request JSON
    comment_edit = forms.validate_comment_edit(comment_edit)

    # Fetch the "old" comment
    old_comment = queries.fetch_comment_by_id(comment_id)

    # Check if does not belong to requesting identity
    if old_comment['identity_id'] != flask.g.identity['id']:
        flask.abort(400,
              'Cannot edit comment: comment belongs to another identity')

    # Check if deleted
    if old_comment['custom_json'].get('deleted'):
        flask.abort(400,
              'Cannot edit comment: comment has been deleted')

    # Update the comment
    raw_comment = queries.update_comment(
        comment_id,
        comment_edit,
        old_comment,
        update_modified=True
    )
    comment = serialize.to_client_comment(raw_comment)
    return flask.jsonify(comment)

def delete(comment_id):
    """Mark a comment as deleted. The comment will still show up in API results,
    but only containing values for it's `id`, `thread_id`, and `parent_id`.

    Note that the actual database record is not deleted. Deletes are handled
    in the same way that edits are: the record is updated in place, and,
    if using the `archive_updated` extension, an archive is made of the old
    record. The `deleted` flag may be used to indicate special rendering of
    deleted comments.
    """
    comment_edit = {
        'text': '',
        'custom_json': {
            'deleted': True,
        }
    }

    # Fetch the "old" comment
    old_comment = queries.fetch_comment_by_id(comment_id)

    # Check if does not belong to requesting identity
    if old_comment['identity_id'] != flask.g.identity['id']:
        flask.abort(400,
              'Cannot delete comment: this comment belongs to another identity')

    # Check if already deleted
    if old_comment['custom_json'].get('deleted'):
        flask.abort(400,
              'Cannot delete comment: comment has already been deleted')

    # Mark the comment as deleted
    result = queries.update_comment(
        comment_id,
        comment_edit,
        old_comment,
        update_modified=True
    )
    return flask.jsonify(result)

def admin_login():
    """View to handle Admin logins."""
    form = auth_forms.LoginForm(flask.request.form)
    if form.validate_on_submit():
        # Login and validate the user.
        user = form.get_user()
        flask_login.login_user(user)
        return 'Logged in successfully.'
    return flask.render_template('login.html', form=form)

def admin_logout():
    """View to handle Admin logouts."""
    flask_login.logout_user()
    return 'Logged out successfully'
