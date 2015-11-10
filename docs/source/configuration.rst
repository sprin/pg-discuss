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

In your Python file, you can override the values in :mod:`pg_discuss.config`,
as well as any default settings in extensions. By using this idiom, you can
read as many (or as few) settings as you want from the environment:

.. code-block::

   MY_VAR = os.environ.get('MY_VAR')

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

csrf_header
-----------

.. automodule:: blessed_extensions.csrf_header
   :members:
   :noindex:
   :exclude-members: CsrfHeaderExt

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

Migrations
==========

Once the database connection is correctly configured, we will need to run
migrations.

.. code-block:: console

   python3.4 main.py db upgrade

Migrations for bundled extensions are located in a separate directory. If
any of the bundled extensions are used, we need to also run:

.. code-block:: console

   python3.4 main.py db upgrade --directory ext_migrations/

Similarly, other extensions you install may have their own migrations. Simply
point the `upgrade` to the directory where they are located.
