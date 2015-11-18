.. _Configuration:

=============
Configuration
=============

Configuration Location
======================

This section describes where configuration files are located, and also which
are read from environment variables by default.

Default Configuration
---------------------

The default configuration is defined in :mod:`pg_discuss.config`. These
defaults provide a fairly featureful deployment that assumes the
bundled `blessed_extensions` package has been installed.

If the default is used, there are some required variables that are read
from environment variables:

 - DATABASE_URL
 - SECRET_KEY
 - SERVER_NAME

You may also choose to put these values in a file instead of environment
variables, if you use a custom configuration file.

Custom Configuration
--------------------

Custom configuration is accomplished through a user-defined Python file.
Creating such a file is not required to use the default configuration. The file
path defaults to `/opt/pg-discuss/local_settings.py`, but can be changed to
another path by setting the `PG_DISCUSS_SETTINGS_FILE` environment variable.
If this file does not exist, it will not be loaded.

In your Python file, you can override the values in :mod:`pg_discuss.config`,
as well as any default settings in extensions. By using this idiom, you can
read as many (or as few) settings as you want from the environment:

.. code-block::

   MY_VAR = os.environ.get('MY_VAR')

Skip ahead to :ref:`Core Config` if you want to see all the options that
can be set in a custom config file.

Migrations
==========

Once the database connection is correctly configured with `DATABASE_URL`, we
will need to run migrations. From within the virtual environment:

.. code-block:: console

   pgd-admin db upgrade

Migrations for bundled extensions are located in a separate directory. If
any of the bundled extensions are used, we need to also run:

.. code-block:: console

   pgd-admin db upgrade --directory ext_migrations/

Similarly, other extensions you install may have their own migrations. Simply
point the `upgrade` to the directory where they are located.

Embedding
=========

Embedding the Isso client, and it's configuration options, are described on
Isso's `Client Configuration`_ page.

.. _Client Configuration`: http://posativ.org/isso/docs/configuration/client/

There are two configuration parameters that are especially important:
`data-isso` and `data-isso-id`.

data-isso
---------

This is the location of the pg-discuss backend. It may be on the same host/port
as the content, or it may be on an entirely different domain. In this example,
we'll assume that:

 - content is served from `https://www.example.com`.
 - pg-discuss is available at `https://www.example.com/pg-discuss`.
 - `embed.min.js` is served from
    `https://www.example.com/pg-discuss/embed.min.js`.

Because all of these are served from the same domain, `www.example.com`, we do
not need to do any extra configuration for cross-domain resource sharing
(CORS).

However, if we wanted to host our content and pg-discuss on different domains,
we can enable CORS on the pg-discuss server. CORS can be enabled via  the
`blessed_cors` extension and the associated `CORS_ORIGINS` setting documented
above, or it can be enabled on the proxy or web server, such as nginx or uwsgi.

data-isso-id
------------

With pg-discuss, it's recommended that you use a unique ID for each thread, for
each page where the comment widget is embedded. This is done by specifying
`data-isso-id`. If you do not specify it, the URI will be used as the thread
identifier, which means if your URI changes, your thread will be lost without
manual updates to the thread ids in the database.

Putting it together
-------------------

Here's what we need to drop in to our HTML page source:

.. code-block:: html

   <script data-isso="https://www.example.com/pg-discuss" src="pg-discuss/embed.min.js"></script>
   <section data-isso-id="my-thread" id="isso-thread"></section>

The `<script>` tag can be placed in the head or body, and the `<section>` tag
defines the element where the widget will render.

For a simple, real-world example, check out the `source`_ of this simplified
`live demo`_.

.. _`source`: view-source:https://pg-discuss.readthedocs.org/en/latest/_static/got_six_weeks.html
.. _`live demo`: https://pg-discuss.readthedocs.org/en/latest/_static/got_six_weeks.html

.. _Core Config:

Core Configuration Options
==========================

.. automodule:: pg_discuss.config
   :members:
   :noindex:
   :exclude-members: get_enabled_extensions, sorted_ext_names

Blessed Extension Configuration Options
=======================================

Default settings for extensions are given here. Extensions are refered to by
their setuptools entrypoint names. Some extensions do not have any configurable
settings and are not shown here.

capture_author
--------------

.. automodule:: blessed_extensions.capture_author
   :members:
   :noindex:
   :exclude-members: CaptureAuthor

csrf_token
----------

.. automodule:: blessed_extensions.csrf_token
   :members:
   :noindex:
   :exclude-members: generate_csrf, validate_csrf, get_csrf_token, some_origin, CsrfTokenExt

markdown_renderer
-----------------

.. automodule:: blessed_extensions.markdown_renderer
   :members:
   :noindex:
   :exclude-members: MarkdownRenderer

mod_email
---------

.. automodule:: blessed_extensions.mod_email
   :members:
   :noindex:
   :exclude-members: ModerationEmail, fetch_admin_emails, send_async_email

profiler
--------

.. automodule:: blessed_extensions.profiler
   :members:
   :noindex:
   :exclude-members: ProfilerExt

validate_comment_len
--------------------

.. automodule:: blessed_extensions.validate_comment_len
   :members:
   :noindex:
   :exclude-members: ValidateCommentLen

.. todo::

   Need to place extension config var defaults to be a member of the class,
   so autodoc can find them.

