"""
Markdown rendering via Mikasa 2, a CFFI wrapper for the Hoedown C Markdown
renderer.

Warning: Mikasa 2 API is currently unstable. This module will need to be
updated upon the next release of Mikasa.
"""
import operator
from pg_discuss import ext
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

class MarkdownComments(ext.OnCommentPreSerialize):
    """Middleware to render comment text as Markdown.
    """

    def __init__(self, app):
        # TODO: Allow flags to be given as a list in a configuration
        # variable. Need to wait until Mikasa 2 releases with stable API.
        render_flags = [HTML_ESCAPE]
        extensions = [EXT_FENCED_CODE]

        # Flags/extensions must be OR'd together to get an integer.
        render_flags_int = reduce(operator.or_, render_flags)
        extensions_int = reduce(operator.or_, extensions)

        renderer = HtmlRenderer(flags=render_flags_int)
        self.markdown = Markdown(renderer, extensions=extensions_int)

    def on_comment_preserialize(self, raw_comment, client_comment, **extras):
        raw_text = raw_comment['text']
        client_comment['text'] = self.markdown.render(raw_text)

