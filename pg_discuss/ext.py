"""Extension base classes.

There are two types of extensions base clases: the Application Extension base
and Hook bases. Base classes can be used as mixins, so that it is possible for
an extensions to implement more than one behavior defined by a base class. As
an extreme example, it is possible to make an extension that implements the
Application Extension base and all Hook bases by subclassing all of the bases
in this module.

The Application Extension base class allows an extension to modify the Flask
app upon initialization, for example, to add routes or request/response
middleware.

The Hook base classes allow an extension to implement a method that is called
when a certain event occurs. To allow Hook APIs to send additional parameters
in the future, all Hook methods must take a `**extras` argument.
"""
import abc
import six

from flask import current_app
import sqlalchemy as sa


class PluginLoadError(Exception):
    pass


class GenericExtBase(object):
    """
    Provide a default class with an __init__ that accepts an app argument.

    To be subclassed by both extension and driver ABCs. This allows
    all plugins to read the configuration from the app.
    """
    def __init__(self, app=None):
        self.app = app


# Driver ABCs
@six.add_metaclass(abc.ABCMeta)
class IdentityPolicy(GenericExtBase):
    """Policy to retrieve an Identity from an identity store, and
    remember/forget the identity (eg, in the browser session).

    The identity may be tied only to a browser session, or may be tied
    to an authenticated user associated with an authentication provider.
    """

    @abc.abstractmethod
    def get_identity(self, request, **extras):
        """Get the identity record associated with the request.
        """

    @abc.abstractmethod
    def forget(self, request, **extras):
        """Forget the identity, if remembered, on subsequent requests.
        """

    @abc.abstractmethod
    def remember(self, request, **extras):
        """Remember the identity for subsequent requests.
        """


@six.add_metaclass(abc.ABCMeta)
class CommentRenderer(GenericExtBase):
    """Driver to render comment text.
    """

    @abc.abstractmethod
    def render(self, text, **extras):
        """Render raw text into another format for display.
        """


# Extension ABCs
@six.add_metaclass(abc.ABCMeta)
class AppExtBase(GenericExtBase):
    """Base class for generic Flask app extensions.

    Such extensions will perform app initialization, possibly
    adding new views.
    """
    @abc.abstractmethod
    def init_app(self, app):
        """Perform app initialization."""


@six.add_metaclass(abc.ABCMeta)
class ValidateComment(GenericExtBase):
    """Mixin class for extensions that validate comment data. Validators
    may mutate the comment data into a valid form.

    Receives an `action` parameter which is either `create` or `edit`.
    """
    @abc.abstractmethod
    def validate_comment(self, comment, action, **extras):
        """Validate a comment dictionary.
        """
    hook_method = validate_comment.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPreCommentInsert(GenericExtBase):
    """Mixin class for extensions that modify the insert statement for new
    comments.
    """
    @abc.abstractmethod
    def on_pre_comment_insert(self, new_comment, **extras):
        """Modify the comment object before inserting.
        """
    hook_method = on_pre_comment_insert.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPostCommentInsert(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    insert.
    """
    @abc.abstractmethod
    def on_post_comment_insert(self, new_comment, **extras):
        """Perform some action with the result of an insert.
        """
    hook_method = on_post_comment_insert.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPreCommentUpdate(GenericExtBase):
    """Mixin class for extensions that modify the update statement for comment
    updates.
    """
    @abc.abstractmethod
    def on_pre_comment_update(self, old_comment, comment_edit, **extras):
        """Modify the update statement for comment updates.
        """
    hook_method = on_pre_comment_update.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPostCommentUpdate(GenericExtBase):
    """Mixin class for extensions that perform some action with the result of an
    update.
    """
    @abc.abstractmethod
    def on_post_comment_update(self, old_comment, new_comment, **extras):
        """Perform some action with the result of an insert.
        """
    hook_method = on_post_comment_update.__name__


@six.add_metaclass(abc.ABCMeta)
class AddCommentFilterPredicate(GenericExtBase):
    """Mixin class for extensions that add a filter predicate to the comment
    fetch.
    """
    @abc.abstractmethod
    def add_comment_filter_predicate(self, **extras):
        """Returns a predicate for the where clause for comment fetches.
        Will be joined with other predicates using AND.
        """
    hook_method = add_comment_filter_predicate.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPreCommentSerialize(GenericExtBase):
    """Mixin class for extensions that want to add fields to the serialized
    comment.
    """
    @abc.abstractmethod
    def on_pre_comment_serialize(self, raw_comment, client_comment, **extras):
        """Add fields to the comment representation to be serialized,
        `client_comment`, from the dictionary representing the raw database
        row, `raw_comment`.
        """
    hook_method = on_pre_comment_serialize.__name__


@six.add_metaclass(abc.ABCMeta)
class OnPreThreadSerialize(GenericExtBase):
    """Mixin class for extensions that want to add fields to the serialized
    thread.
    """
    @abc.abstractmethod
    def on_pre_thread_serialize(self, raw_thread, comment_seq, client_thread,
                                **extras):
        """Add fields to the thread representation to be serialized,
        `client_thread`, from the dictionary representing the raw database row,
        `raw_thread`.
        """
    hook_method = on_pre_thread_serialize.__name__


@six.add_metaclass(abc.ABCMeta)
class OnNewCommentResponse(GenericExtBase):
    """Mixin class for extensions that want to process the response of the new
    comment view.

    A common case is to set cookies or other headers using the value of the
    newly created comment.
    """
    @abc.abstractmethod
    def on_new_comment_response(self, resp, raw_comment, client_comment,
                                **extras):
        """Process the response of the new comment view. Both the 'raw' comment
        and the comment formatted for the client are given as arguments.
        """
    hook_method = on_new_comment_response.__name__


# Extension utility functions
def exec_hooks(ext_class, *args, **kwargs):
    """Execute the hook function associated with the extension mixin class.
    Note that this allows for extensions to subclass multiple hook mixins.

    Returns the list of results obtained from calling all relevant
    extensions in order. Similar to stevedore's `ExtensionManager.map()`,
    however, we only call on extensions that are an instance of the base class
    given.
    """

    def execute_hook(ext, ext_class, *args, **kwargs):
        """Invoke the hook associated with a given extension class on the
        extension object."""
        return getattr(ext.obj, ext_class.hook_method)(*args, **kwargs)

    results = []
    for ext in current_app.ext_mgr.extensions:
        if isinstance(ext.obj, ext_class):
            results.append(execute_hook(ext, ext_class, *args, **kwargs))

    return results


def exec_init_app(app):
    """Execute the init_app for any instance of AppExtBase.
    """

    for ext in app.ext_mgr.extensions:
        if isinstance(ext.obj, AppExtBase):
            ext.obj.init_app(app)


def fail_on_ext_load(manager, entrypoint, exception):
    """Function to be used as `on_load_failure_callback` for stevedore.

    Raise an exception that includes the traceback from the failed
    plugin load.
    """
    import traceback
    msg = (
        'Error loading plugin {0}\n'
        'Plugin load error traceback:\n{1}'
        .format(entrypoint, traceback.format_exc()))
    raise PluginLoadError(msg)


def exec_filter_hooks(ext_class, stmt, *args, **kwargs):
    """Execute query filter hooks and collect all the returned predicates
    in an AND expression to be used in the WHERE clause.
    """
    predicates = exec_hooks(ext_class, *args, **kwargs)
    stmt = stmt.where(sa.and_(*predicates))
    return stmt
