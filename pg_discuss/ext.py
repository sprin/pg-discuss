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
class DoOnUpdateBase(GenericExtBase):
    """Base class for extensions that perform some action with the result of an
    update.
    """

    @abc.abstractmethod
    def do_on_update(self, old_comment, new_comment):
        """Perform some action with the result of an insert.
        """

@six.add_metaclass(abc.ABCMeta)
class ModifyUpdateStmtBase(GenericExtBase):
    """Base class for extensions that modify the update statement for comment
    updates.
    """
    @abc.abstractmethod
    def modify_update_stmt(self, old_comment, comment_edit, stmt):
        """Modify the update statement for comment updates.

        Returns a new SQL Alchemy statement.
        """

@six.add_metaclass(abc.ABCMeta)
class ModifyInsertStmtBase(GenericExtBase):
    """Base class for extensions that modify the insert statement for new
    comments.
    """
    @abc.abstractmethod
    def modify_insert_stmt(self, new_comment, stmt):
        """Modify the insert statement for comment updates.

        Returns a new SQL Alchemy statement.
        """

@six.add_metaclass(abc.ABCMeta)
class ModifyInsertStmtBase(GenericExtBase):
    """Base class for extensions that perform some action with the result of an
    insert.
    """
    @abc.abstractmethod
    def do_on_insert(self, new_comment):
        """Perform some action with the result of an insert.
        """

def map_do_on_update(old_comment, new_comment):

    def _do_on_update(ext, old_comment, new_comment):
        if isinstance(ext.plugin, DoOnUpdateBase):
            ext.obj.do_on_update(old_comment, new_comment)

    current_app.mgr.map(_do_on_update, old_comment, new_comment)
