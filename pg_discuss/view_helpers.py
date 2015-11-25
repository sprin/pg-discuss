"""
Helpers for view functions.
"""
import flask


def after_this_request(f):
    """Register a function to run once the request complete.
    The function will receive the response as a callback.
    """
    if not hasattr(flask.g, 'after_request_callbacks'):
        flask.g.after_request_callbacks = []
    flask.g.after_request_callbacks.append(f)
    return f
