.. _Extensions:

=============================
Extension and Driver Overview
=============================

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

An `IdentityPolicy` driver implements the policy for associating requests with
identities. Cookies are used to "remember" identities.

The `IdentityPolicy` plugpoint allows for a wide range of authentication
mechanisms to be implemented. Some possibilities include OAuth 2, traditional
username/password logon, Kerberos.

See :class:`~pg_discuss.ext.IdentityPolicy` for the base class, and
:class:`~pg_discuss.ext.IdentityPolicyManager` for the middleware class that
executes the policy.

CommentRenderer
---------------

A `CommentRenderer` driver renders the raw text of a comment into a format
for presentation, typically plain or HTML. The choice of renderer will affect
the accepted formats for comment text input, such as plain, Markdown, or HTML.

This driver plays an important role in XSS prevention: the driver must ensure
that output is sufficiently sanitized or escaped.

See :class:`~pg_discuss.ext.CommentRenderer` for the base class, and
:func:`~pg_discuss.serialize:_to_client_comment` for the invocation of the
renderer.

JSONEncoder
-----------

The `JSONEncoder` is used to encode the comment object (the text and metadata)
into a JSON object. Different implementations may choose to handle certain
types, such as dates, differently. Implementations should subclass
`simplejson.JSONEncoder`_ and define a `default`_ method.

.. todo::

   Follow up on subclassing issue with simplejson:
   https://github.com/simplejson/simplejson/issues/124

.. _simplejson.JSONEncoder: https://simplejson.readthedocs.org/en/latest/#simplejson.JSONEncoder
.. _default: https://simplejson.readthedocs.org/en/latest/#simplejson.JSONEncoder.default

Extensions
==========

Extension plugins use hooks to add additional functionality. Unlike drivers,
no extensions are required for the application to run. Extensions can
participate in app initialization to configure new views or to hook in to
the Flask framework's events. Extensions can also hook in to custom events
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

 - :meth:`~pg_discuss.ext.ValidateComment.validate_comment`: validate comment, possibly mutating
   into valid form.  Receives an `action` parameter which is either `create` or
   `edit`.
 - :meth:`~pg_discuss.ext.OnPreCommentInsert.on_pre_comment_insert`: modify the
   comment before inserting into the database.
 - :meth:`~pg_discuss.ext.OnPostCommentInsert.on_post_comment_insert`: perform
   some action with the result of a comment insert.
 - :meth:`~pg_discuss.ext.OnPreCommentUpdate.on_pre_comment_update`: modify the
   commment before updating in the database.
 - :meth:`~pg_discuss.ext.OnPostCommentUpdate.on_post_comment_update`: perform
   some action with the result of a comment update.
 - :meth:`~pg_discuss.ext.AddCommentFilterPredicate.add_comment_filter_predicate`:
   return an SQLAlchemy filter predicate to be appended to the select statement
   used to fetch comment.
 - :meth:`~pg_discuss.ext.OnPreCommentSerialize.on_pre_comment_serialize`: add
   fields to the "client comment" object to be serialized.
 - :meth:`~pg_discuss.ext.OnPreThreadSerialize.on_pre_thread_serialize`: add
   fields to the "client thread" object to be serialized.
 - :meth:`~pg_discuss.ext.OnNewCommentResponse.on_new_comment_response`: modify
   the response returned from the new comment view, with the "raw comment" and
   "client comment" in the context.
