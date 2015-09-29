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
their setuptools entrypoint names.

validate_comment_len
--------------------

.. automodule:: blessed_extensions.validate_comment_len
   :members:
   :noindex:
   :exclude-members: ValidateCommentLen

.. todo::

   Need to place extension config var defaults to be a member of the class,
   so autodoc can find them.
