from __future__ import print_function
import sys
import hashlib
import base64

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def sha256hash(content):
    return hashlib.sha256(content).hexdigest()

def base64encode(content):
    return base64.b64encode(content)