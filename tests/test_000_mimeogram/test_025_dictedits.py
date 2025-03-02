# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for dictedits module. '''

# pylint: disable=useless-parent-delegation


import pytest

from . import cache_import_module


def test_000_edit_protocol( ):
    ''' Edit protocol defines expected interface. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    assert hasattr( dictedits.Edit, 'address' )
    assert hasattr( dictedits.Edit, '__call__' )


def test_100_simple_edit( ):
    ''' SimpleEdit applies basic dictionary edits. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    config = { }
    edit = dictedits.SimpleEdit( address = ( 'a', 'b' ), value = 42 )
    edit( config )
    assert config == { 'a': { 'b': 42 } }


def test_110_simple_edit_existing( ):
    ''' SimpleEdit modifies existing nested structures. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    config = { 'a': { 'b': 1, 'c': 2 } }
    edit = dictedits.SimpleEdit( address = ( 'a', 'b' ), value = 42 )
    edit( config )
    assert config == { 'a': { 'b': 42, 'c': 2 } }


def test_200_elements_entry_edit( ):
    ''' ElementsEntryEdit applies edits to array elements. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    config = { 'items': [ { 'id': 1 }, { 'id': 2 } ] }
    edit = dictedits.ElementsEntryEdit(
        address = ( 'items', ),
        editee = ( 'value', 42 ),
        identifier = ( 'id', 1 ) )
    edit( config )
    assert config == {
        'items': [ { 'id': 1, 'value': 42 }, { 'id': 2 } ] }


def test_210_elements_entry_edit_all( ):
    ''' ElementsEntryEdit modifies all elements without identifier. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    config = { 'items': [ { 'id': 1 }, { 'id': 2 } ] }
    edit = dictedits.ElementsEntryEdit(
        address = ( 'items', ),
        editee = ( 'value', 42 ) )
    edit( config )
    assert config == {
        'items': [ { 'id': 1, 'value': 42 }, { 'id': 2, 'value': 42 } ] }


def test_300_edit_errors( ):
    ''' Edits raise appropriate errors. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    config = { }
    edit = dictedits.SimpleEdit( address = ( 'a', 'b' ), value = 42 )
    edit( config ) # Should create missing parts
    config = { 'items': [ { } ] }
    edit = dictedits.ElementsEntryEdit(
        address = ( 'items', ),
        editee = ( 'value', 42 ),
        identifier = ( 'id', 1 ) )
    with pytest.raises( exceptions.EntryAssertionFailure ):
        edit( config )


def test_400_dereference( ):
    ''' Edit base class dereference method works correctly. '''
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    config = { 'a': { 'b': 42 } }
    edit = dictedits.SimpleEdit( address = ( 'a', 'b' ), value = 0 )
    assert edit.dereference( config ) == 42
    with pytest.raises( exceptions.AddressLocateFailure ):
        edit.dereference( { } )
