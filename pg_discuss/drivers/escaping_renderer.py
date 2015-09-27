import markupsafe

from .. import ext


class EscapingRenderer(ext.CommentRenderer):
    """Renderer driver that escapes using HTML entity encoding.

    This neutralizes all markup contained in the comment text.
    """

    def render(self, text, **extras):
        """Render to HMTL entity-encoded text.
        """
        return markupsafe.escape(text)
