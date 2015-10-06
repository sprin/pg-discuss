import operator

import misaka

from pg_discuss import _compat
from pg_discuss import ext

#: Markdown rendering flags. These flags have integer values: the default of
#: "2" is for the `HTML_ESCAPE` flag.
#: See: http://misaka.61924.nl/api/
MARKDOWN_RENDER_FLAGS = [misaka.HTML_ESCAPE, misaka.HTML_HARD_WRAP]
#: Markdown extension flags. These flags have integer values: the default of
#: "2" is for the `EXT_FENCED_CODE` extension.
#: See: http://misaka.61924.nl/api/
MARKDOWN_EXTENSION_FLAGS = [misaka.EXT_FENCED_CODE]


class MarkdownRenderer(ext.CommentRenderer):
    """
    Markdown render driver via Mikasa 2, a CFFI wrapper for the Hoedown C
    Markdown renderer.

    This renderer escapes any HTML that does not originate from the allowed
    Markup syntax.
    """

    def __init__(self, app=None):
        # TODO: Allow flags to be given as a list in a configuration
        # variable. Need to wait until Mikasa 2 releases with stable API.
        app.config.setdefault('MARKDOWN_RENDER_FLAGS',
                              MARKDOWN_RENDER_FLAGS)
        app.config.setdefault('MARKDOWN_EXTENSION_FLAGS',
                              MARKDOWN_EXTENSION_FLAGS)

        # Flags/extensions must be OR'd together to get an integer.
        render_flags_int = _compat.reduce(operator.or_,
                                          app.config['MARKDOWN_RENDER_FLAGS'])
        extensions_int = _compat.reduce(operator.or_,
                                        app.config['MARKDOWN_EXTENSION_FLAGS'])

        renderer = misaka.HtmlRenderer(flags=render_flags_int)
        self.markdown = misaka.Markdown(renderer, extensions=extensions_int)

    def render(self, text, **extras):
        """Render Markdown to HTML.
        """
        return self.markdown.render(text)
