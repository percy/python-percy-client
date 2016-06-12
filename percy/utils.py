from __future__ import print_function
import sys
import hashlib
import base64

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def to_unicode(content):
    # TODO: considering using the 'six' library for this, for now just do something simple.
    if sys.version_info >= (3,0):
        return str(content)
    elif sys.version_info < (3,0):
        return unicode(content)

def sha256hash(content):
    if _is_unicode(content):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def base64encode(content):
    if _is_unicode(content):
        content = content.encode('utf-8')
    return to_unicode(base64.b64encode(content))

def _is_unicode(content):
    if (sys.version_info >= (3,0) and isinstance(content, str)
        or sys.version_info < (3,0) and isinstance(content, unicode)):
        return True
    return False
