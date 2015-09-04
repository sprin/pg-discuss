"""
Markdown rendering via Mikasa 2, a CFFI wrapper for the Hoedown C Markdown
renderer.

Warning: Mikasa 2 API is currently unstable. This module will need to be
updated upon the next release of Mikasa.
"""
import operator
from pg_discuss import ext
from pg_discuss import _compat
from misaka import (
    Markdown,
    HtmlRenderer,
    EXT_FENCED_CODE,
    HTML_ESCAPE,
)
try:
    reduce
except NameError:
    from functools import reduce

class MarkdownRenderer(ext.CommentRenderer):
    """Renderer driver to render comment text as Markdown.

    This renderer escapes any HTML that does not originate from the allowed
    Markup syntax.
    """

    def __init__(self, app=None):
        self.app = app
        # TODO: Allow flags to be given as a list in a configuration
        # variable. Need to wait until Mikasa 2 releases with stable API.
        render_flags = [HTML_ESCAPE]
        extensions = [EXT_FENCED_CODE]

        # Flags/extensions must be OR'd together to get an integer.
        render_flags_int = reduce(operator.or_, render_flags)
        extensions_int = reduce(operator.or_, extensions)

        renderer = HtmlRenderer(flags=render_flags_int)
        self.markdown = Markdown(renderer, extensions=extensions_int)

    def render(self, text, **extras):
        """Render Markdown to HTML.
        """
        return self.markdown.render(text)

class EscapingRenderer(ext.CommentRenderer):
    """Renderer driver that escapes using HTML entity encoding.

    This neutralizes all markup contained in the comment text.
    """

    def render(self, text, **extras):
        """Render to HMTL entity-encoded text.
        """
        return _compat.escape(text)
