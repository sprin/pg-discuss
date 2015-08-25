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
class ModifyInsertStmtMixin(GenericExtBase):
    """Mixin class for extensions that modify the insert statement for new
    comments.
    """
    hook_name = 'modify_insert_stmt'

    @abc.abstractmethod
    def modify_insert_stmt(self, new_comment, stmt):
        """Modify the insert statement for comment updates.

        Returns a new SQL Alchemy statement.
        """


@six.add_metaclass(abc.ABCMeta)
class DoOnInsertMixin(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    insert.
    """
    hook_name = 'do_on_insert'

    @abc.abstractmethod
    def do_on_insert(self, new_comment):
        """Perform some action with the result of an insert.
        """


@six.add_metaclass(abc.ABCMeta)
class ModifyUpdateStmtMixin(GenericExtBase):
    """Mixin class for extensions that modify the update statement for comment
    updates.
    """
    hook_name = 'modify_update_stmt'

    @abc.abstractmethod
    def modify_update_stmt(self, old_comment, comment_edit, stmt):
        """Modify the update statement for comment updates.

        Returns a new SQL Alchemy statement.
        """


@six.add_metaclass(abc.ABCMeta)
class DoOnUpdateMixin(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    update.
    """
    hook_name = 'do_on_update'

    @abc.abstractmethod
    def do_on_update(self, old_comment, new_comment):
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
