======================
Extensions and Drivers
======================

pg-discuss contains a small set of "core" modules whose primary responsibility
is to provide the framework for pluggable components. Plugins are responsible
for implementing features like capturing custom fields from the client, comment
validation, rendering comments in a markup language, security and
authentication middleware, JSON encoding, and adding new endpoints. There are
two types of plugins: drivers and extensions.

Drivers
=======

Driver plugins implement functionality that is required by the core
application. There are several types of drivers, and only one driver plugin may
be enabled for each type of driver.

IdentityPolicy
--------------

An `IdentityPolicy` driver implements the authentication policy by associating
requests with identities. Cookies are used to "remember" identities.

The `IdentityPolicy` plugpoint allows for a wide range of authentication
mechanisms to be implemented. Some possibilities include OAuth 2, traditional
username/password logon, Kerberos.

CommentRenderer
---------------

A `CommentRenderer` driver renders the raw text of a comment into a format
for presentation, typically plain or HTML. The choice of renderer will affect
the accepted formats for comment text input, such as plain, Markdown, or HTML.

This driver plays an important role in XSS prevention: the driver must ensure
that output is sufficiently sanitized or escaped.

JSONEncoder
-----------

The JSONEncoder is used to encode the comment object (the text and metadata)
into a JSON object. Different implementations may choose to handle certain
types, such as dates, differently.

Extensions
==========

Extension plugins use hooks to add additional functionality. Unlike drivers,
no extensions are required for the application to run. Extensions can
participate in to app initialization to configure new views or to hook in to
the Flask frameworks events. Extensions can also hook in to custom events
defined by pg-discuss.

A quick summary of available hooks that are likely to be useful to extensions
follows.

Flask hooks
-----------

 - add_url_rule: register a URL routing rule.
 - before_request: register a function to run before each request.
 - after_request: register a function to run after each request.
 - register_error_handler: register a function to handle a given error code or
   arbitrary Exception.

See `Flask API specification`_ for more detail.

.. _Flask API specification: http://flask.pocoo.org/docs/0.10/api/

pg-discuss hooks
----------------

 - validate_comment: validate comment, possibly mutating into valid form.
 - on_pre_comment_insert: modify the comment before inserting into the
   database.
 - on_post_comment_insert: perform some action with the result of a comment
   insert.
 - on_pre_comment_update: modify the commment before updating in the database.
 - on_post_comment_update: perform some action with the result of a comment update.
 - on_pre_comment_fetch: return a filter clause to be appended to the select
   statement used to fetch comment.
 - on_comment_pre_serialize: add fields to the "client comment" object to be
   serialized.
 - on_thread_pre_serialize: add fields to the "client thread" object to be
   serialized.
 - on_comment_collection_preserialize: add or modify the comment collection
   object, whose JSON representation is the response to a fetch.
 - on_new_comment_response: modify the response returned from the new comment
   view, with the "raw comment" and "client comment" in the context.

TOOD: merge on_thread_preserialize with on_comment_collection_preserialize

TODO: link to Sphinx API docs.
