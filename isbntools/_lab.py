# -*- coding: utf-8 -*-
"""isbntools helpers file."""

# DON'T USE! in the future this will be in 'isbnlib'

import os
import sys

from isbnlib.dev.bouth23 import b, b2u3

WINDOWS = os.name == 'nt'


def sprint(content):
    """Smart print function so that redirection works... (see issue 75)."""
    if WINDOWS:  # pragma: no cover
        # the `print` function detects the appropriate codec
        # (Windows terminal doesn't use UTF-8)
        # s = content + '\n'
        # s = content.encode("utf-8")
        print(b(content))
        # sys.stdout.write(s)
    else:
        # stdout gets UTF-8
        s = content + '\n'
        sys.stdout.write(b2u3(s))
