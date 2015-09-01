"""Extension base classes.

There are two types of extensions base clases: the Application Extension base
and Hook bases. Base classes can be used as mixins, so that it is possible for
an extensions to implement more than one behavior defined by a base class. As an
extreme example, it is possible to make an extension that implements the
Application Extension base and all Hook bases by subclassing all of the bases in
this module.

The Application Extension base class allows an extension to modify the Flask app
upon initialization, for example, to add routes or request/response middleware.

The Hook base classes allow an extension to implement a method that is called
when a certain event occurs. To allow Hook APIs to send additional parameters in
the future, all Hook methods must take a `**extras` argument.
"""
import abc
import six

from flask import current_app

class PluginLoadError(Exception):
    pass


class GenericExtBase(object):
    """
    Provide a default class with an __init__ that accepts an app argument.
    """
    def __init__(self, app=None):
        self.app = app

@six.add_metaclass(abc.ABCMeta)
class AppExtBase(GenericExtBase):
    """Base class for generic Flask app extensions.

    Such extensions will perform app initialization, possibly
    adding new views.
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    @abc.abstractmethod
    def init_app(self, app):
        """Perform app initialization."""


@six.add_metaclass(abc.ABCMeta)
class OnPreInsert(GenericExtBase):
    """Mixin class for extensions that modify the insert statement for new
    comments.
    """
    hook_name = 'on_pre_insert'

    @abc.abstractmethod
    def on_pre_insert(self, stmt_wrapper, new_comment, **extras):
        """Modify the insert statement for comment updates.

        The SQL Alchemy statement can be modified with
        `stmt_wrapper.stmt = ...`.
        """


@six.add_metaclass(abc.ABCMeta)
class OnPostInsert(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    insert.
    """
    hook_name = 'on_post_insert'

    @abc.abstractmethod
    def on_post_insert(self, new_comment, **extras):
        """Perform some action with the result of an insert.
        """


@six.add_metaclass(abc.ABCMeta)
class OnPreUpdate(GenericExtBase):
    """Mixin class for extensions that modify the update statement for comment
    updates.
    """
    hook_name = 'on_pre_update'

    @abc.abstractmethod
    def on_pre_update(self, stmt_wrapper, old_comment, comment_edit, **extras):
        """Modify the update statement for comment updates.

        The SQL Alchemy statement can be modified with
        `stmt_wrapper.stmt = ...`.
        """


@six.add_metaclass(abc.ABCMeta)
class OnPostUpdate(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    update.
    """
    hook_name = 'on_post_update'

    @abc.abstractmethod
    def on_post_update(self, old_comment, new_comment, **extras):
        """Perform some action with the result of an insert.
        """

@six.add_metaclass(abc.ABCMeta)
class ValidateComment(GenericExtBase):
    """Mixin class for extensions that validate comment data. Validators
    may mutate the comment data into a valid form.
    """
    hook_name = 'validate_comment'

    @abc.abstractmethod
    def validate_comment(self, comment, **extras):
        """Validate a comment dictionary.
        """

@six.add_metaclass(abc.ABCMeta)
class OnPreFetch(GenericExtBase):
    """Mixin class for extensions that modify the select statement for
    comment fetches.
    """
    hook_name = 'on_pre_fetch'

    @abc.abstractmethod
    def on_pre_fetch(self, stmt_wrapper, **extras):
        """Modify the select statement for comment fetches.

        The SQL Alchemy statement can be modified with
        `stmt_wrapper.stmt = ...`.
        """

@six.add_metaclass(abc.ABCMeta)
class OnCommentPreSerialize(GenericExtBase):
    """Mixin class for extensions that want to add fields to the serialized
    comment.
    """
    hook_name = 'on_comment_preserialize'

    @abc.abstractmethod
    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        """Add fields to the comment representation to be serialized,
        `client_comment`, from the dictionary representing the raw database row,
        `raw_comment`.
        """

@six.add_metaclass(abc.ABCMeta)
class OnThreadPreSerialize(GenericExtBase):
    """Mixin class for extensions that want to add fields to the serialized
    thread.
    """
    hook_name = 'on_thread_preserialize'

    @abc.abstractmethod
    def on_comment_preserialize(self, raw_thread, client_thread, **extras):
        """Add fields to the thread representation to be serialized,
        `client_thread`, from the dictionary representing the raw database row,
        `raw_thread`.
        """

def exec_hooks(ext_class, *args, **kwargs):
    """Execute the hook function associated with the extension mixin class.
    Note that this allows for extensions to subclass multiple hook mixins.

    Returns the list of results obtained from calling all relevant
    extensions in order. Similar to stevedore's `ExtensionManager.map()`,
    however, we only call on extensions that are an instance of the base class
    given.
    """

    def execute_hook(ext, ext_class, *args, **kwargs):
        return getattr(ext.obj, ext_class.hook_name)(*args, **kwargs)

    results = []
    for ext in current_app.ext_mgr.extensions:
        if isinstance(ext.obj, ext_class):
            results.append(execute_hook(ext, ext_class, *args, **kwargs))

    return results

def fail_on_ext_load(manager, entrypoint, exception):
    """Function to be used as `on_load_failure_callback` for stevedore.

    Raise an exception that includes the traceback from the failed
    plugin load.
    """
    import traceback
    msg = (
        'Error loading plugin {0}\n'
        'Plugin load error traceback:\n{1}'.format( entrypoint,
            traceback.format_exc()
        ))
    raise PluginLoadError(msg)

class StatementWrapper(object):
    """Wrapper for SQL Alchemy statements to allow statements to be passed to
    functions that can mutate them.
    """

    def __init__(self, stmt):
        self.stmt = stmt

def exec_query_hooks(ext_class, stmt, *args, **kwargs):
    """Execute query hooks. Wraps the SQL Alchemy statement in a container
    object to allow hooks to mutate the statement.
    """
    stmt_wrapper = StatementWrapper(stmt)
    exec_hooks(ext_class, stmt_wrapper, *args, **kwargs)
    return stmt_wrapper.stmt
