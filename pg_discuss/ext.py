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
    def on_pre_insert(self, new_comment, stmt, **extras):
        """Modify the insert statement for comment updates.

        Returns a new SQL Alchemy statement.
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
    def on_pre_update(self, old_comment, comment_edit, stmt, **extras):
        """Modify the update statement for comment updates.

        Returns a new SQL Alchemy statement.
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


def exec_hooks(ext_class, *args, **kwargs):
    """Execute the hook function associated with the extension mixin class.
    Note that this allows for extensions to subclass multiple hook mixins.
    """

    def execute_hook(ext, *args, **kwargs):
        if isinstance(ext.obj, ext_class):
            getattr(ext.obj, ext.plugin.hook_name)(*args, **kwargs)

    current_app.ext_mgr.map(execute_hook, *args, **kwargs)
