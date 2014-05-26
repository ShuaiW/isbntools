# -*- coding: utf-8 -*-

"""Rename file using metadata."""

import sys
import string
import logging
from ._helpers import last_first
from ..bouth23 import u, b2u3
from .. import config
from ._files import File, cwdfiles
from .. import EAN13, get_isbnlike, meta


LOGGER = logging.getLogger(__name__)

DEFAULT_PATT = '{firstAuthorLastName}{year}_{title}_{isbn}'
PATTERN = config.options.get('REN_FORMAT', DEFAULT_PATT)


def checkpattern(pattern):
    """Check the validity of pattern for renaming a file."""
    placeholders = ('{authorsFullNames}', '{authorsLastNames}',
                    '{firstAuthorLastName}', '{year}', '{publisher}',
                    '{title}', '{isbn}', '{language}')
    tocheck = pattern[:]

    placeholderfound = False
    for placeholder in placeholders:
        if placeholder in tocheck:
            tocheck = tocheck.replace(placeholder, '')
            placeholderfound = True
    if not placeholderfound or '{' in tocheck:
        LOGGER.warning('Not valid pattern %s', pattern)
        return False

    validchars = '-_.,() {0}{1}'.format(string.ascii_letters, string.digits)

    for char in tocheck:
        if char not in validchars:
            LOGGER.warning('Invalid character in pattern (%s)', char)
            return False
    return True


PATTERN = PATTERN if checkpattern(PATTERN) else DEFAULT_PATT


def newfilename(metadata, pattern=PATTERN):
    """Return a new file name created from book metadata."""
    pattern = pattern if pattern else PATTERN
    for key in metadata.keys():
        if not metadata[key]:
            metadata[key] = u('UNKNOWN')

    d = {
        'authorsFullNames': ','.join(metadata['Authors']),
        'year': metadata['Year'],
        'publisher': metadata['Publisher'],
        'title': metadata['Title'],
        'language': metadata['Language'],
        'isbn': metadata['ISBN-13']
    }

    authorslastnames = [last_first(authorname)['last']
                        for authorname in metadata['Authors']]
    d['authorsLastNames'] = ','.join(authorslastnames)
    d['firstAuthorLastName'] = authorslastnames[0]
    if d['title'] == u('UNKNOWN') or d['isbn'] == u('UNKNOWN'):
        LOGGER.critical('Not enough metadata')
        return

    # cutoff title at 65
    cutoff = min(len(d['title']), 65)
    d['title'] = d['title'][:cutoff]

    try:
        formatted = u(pattern).format(**d)
        return cleannewname(formatted)
    except KeyError as e:
        LOGGER.warning('Error with placeholder: %s', e)
        return


def cleannewname(newname):
    """Strip '.,_' from newname."""
    return newname.strip().strip('.,_')


def get_isbn(filename):
    """Extract the ISBN from file's name."""
    isbn = EAN13(get_isbnlike(filename, level='normal')[0])
    if not isbn:
        sys.stderr.write('no ISBN found in name of file %s \n' % filename)
        return
    return isbn


def renfile(filename, isbn, service, pattern=PATTERN):
    """Rename file with associate ISBN."""
    service = service if service else 'default'
    metadata = meta(isbn, service)
    newname = newfilename(metadata, pattern)
    if not newname:
        sys.stderr.write('%s NOT renamed \n' % filename)
        return
    oldfile = File(filename)
    ext = oldfile.ext
    newbasename = b2u3(newname + ext)
    oldbasename = oldfile.basename
    if oldfile.mkwinsafe(newbasename) == oldbasename:
        return True
    success = oldfile.baserename(newbasename)
    if success:
        try:
            sys.stdout.write('%s renamed to %s \n' %
                             (oldbasename, oldfile.basename))
        except:
            pass
        return True
    return


def rencwdfiles(fnpatt="*", service='default', pattern=PATTERN):
    """Rename cwd files with a ISBN in their filenames and within fnpatt."""
    files = [(get_isbn(f), f) for f in cwdfiles(fnpatt) if get_isbn(f)]
    for isbn, f in files:
        renfile(f, isbn, service, pattern)
    return True
