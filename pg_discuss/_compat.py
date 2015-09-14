"""
Python 2/3 compatibility helpers.

From flask_wtf._compat:
https://github.com/lepture/flask-wtf/blob/HEAD/flask_wtf/csrf.py
"""
import sys
import urllib
try:
    from urlparse import urlparse
except ImportError: # pragma: no cover
    # python 3
    from urllib.parse import urlparse

PY3 = sys.version_info[0] == 3
PYPY = hasattr(sys, 'pypy_version_info')

if PY3: # pragma: no cover
    text_type = str
    string_types = (str,)
    unquote = urllib.parse.unquote
else: # pragma: no cover
    text_type = unicode
    string_types = (str, unicode)
    unquote = urllib.unquote

def to_bytes(text):
    """Transform string to bytes."""
    if isinstance(text, text_type):
        text = text.encode('utf-8')
    return text

def to_unicode(input_bytes, encoding='utf-8'):
    """Decodes input_bytes to text if needed."""
    if not isinstance(input_bytes, string_types):
        input_bytes = input_bytes.decode(encoding)
    return input_bytes
