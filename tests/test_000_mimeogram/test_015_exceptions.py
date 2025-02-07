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


''' Tests for exceptions module. '''


import pytest

from . import cache_import_module


def test_000_exception_hierarchy( ):
    ''' Exception hierarchy is properly structured. '''
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    assert issubclass( exceptions.Omnierror, exceptions.Omniexception )
    assert issubclass( exceptions.Omnierror, Exception )
    assert issubclass( exceptions.Omniexception, BaseException )


def test_010_address_locate_failure( ):
    ''' AddressLocateFailure provides expected behavior. '''
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    subject = 'test_subject'
    address = ( 'part1', 'part2' )
    part = 'part3'
    exc = exceptions.AddressLocateFailure( subject, address, part )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, LookupError )
    assert subject in str( exc )
    assert str( address ) in str( exc )
    assert part in str( exc )


def test_020_entry_assertion_failure( ):
    ''' EntryAssertionFailure provides expected behavior. '''
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    subject = 'test_subject'
    name = 'test_name'
    exc = exceptions.EntryAssertionFailure( subject, name )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, AssertionError )
    assert isinstance( exc, KeyError )
    assert subject in str( exc )
    assert name in str( exc )


def test_030_operation_invalidity( ):
    ''' OperationInvalidity provides expected behavior. '''
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    subject = 'test_subject'
    name = 'test_operation'
    exc = exceptions.OperationInvalidity( subject, name )
    assert isinstance( exc, exceptions.Omnierror )
    assert isinstance( exc, RuntimeError )
    assert subject in str( exc )
    assert name in str( exc )


def test_100_exception_immutability( ):
    ''' Exceptions are immutable. '''
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    with pytest.raises( Exception ):
        exceptions.OperationInvalidity.new_attribute = 'value'


# def test_200_exception_attribute_visibility( ):
#     ''' Exception attribute visibility is properly controlled. '''
#     exceptions = cache_import_module( 'mimeogram.__.exceptions' )
#
#     class TestException( exceptions.Omniexception ):
#         _attribute_visibility_includes_ = frozenset( ( 'visible_attr', ) )
#
#         def __init__( self ):
#             self.visible_attr = 'visible'
#             self.hidden_attr = 'hidden'
#
#     exc = TestException( )
#     assert hasattr( exc, 'visible_attr' )
#     assert exc.visible_attr == 'visible'
#     assert not hasattr( exc, 'hidden_attr' )
