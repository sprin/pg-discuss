"""The `blessed_extensions` package contains extensions and drivers which are
bundled with pg-discuss.

Installation is optional, but recommended since the
functionality contained in the core is probably too minimal for most
installations. However, some deployments may want to supply all of their own
drivers and extensions, and in this case `blessed_extensions` does not need
to be installed.

pg-discuss uses uses setuptools entrypoints for discovery/loading of extensions
and drivers. The entrypoints are defined in `setup.py`.
"""
