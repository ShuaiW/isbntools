#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ..metadata import query
from nose.tools import assert_equals, assert_raises


# nose tests
def test_query():
    assert_equals(query('9781849692342', 'goog'), None)
    assert_equals(len(repr(query('9781849692342', 'goob'))), 209)
    assert_raises(Exception, query, '9781849692342', 'wcat')
    assert_equals(len(repr(query('9780321534965', 'wcat'))), 257)
    assert_equals(len(repr(query('9780321534965'))), 257)
