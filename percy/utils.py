from __future__ import print_function
import sys
import hashlib
import base64

# TODO: considering using the 'six' library here, but for now just do something simple.

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def sha256hash(content):
    if _is_unicode(content):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def base64encode(content):
    if _is_unicode(content):
        content = content.encode('utf-8')
    return base64.b64encode(content).decode('utf-8')

def _is_unicode(content):
    if (sys.version_info >= (3,0) and isinstance(content, str)
        or sys.version_info < (3,0) and isinstance(content, unicode)):
        return True
    return False
