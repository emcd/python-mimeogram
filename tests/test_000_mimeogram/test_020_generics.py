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


''' Tests for generics module. '''


import pytest

from . import cache_import_module


def test_000_type_variables( ):
    ''' Type variables are properly defined. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    assert hasattr( generics, 'T' )
    assert hasattr( generics, 'U' )
    assert hasattr( generics, 'E' )
    assert issubclass( Exception, generics.E.__bound__ )


def test_100_result_value( ):
    ''' Value variant of Result behaves correctly. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    result = generics.Value( 42 )
    assert result.is_value( )
    assert not result.is_error( )
    assert result.extract( ) == 42


def test_110_result_error( ):
    ''' Error variant of Result behaves correctly. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    error = ValueError( 'test error' )
    result = generics.Error( error )
    assert result.is_error( )
    assert not result.is_value( )
    with pytest.raises( ValueError ) as exc_info:
        result.extract( )
    assert exc_info.value is error


def test_200_result_transform_value( ):
    ''' Value results transform correctly. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    result = generics.Value( 42 )
    transformed = result.transform( lambda x: x * 2 )
    assert transformed.is_value( )
    assert transformed.extract( ) == 84


def test_210_result_transform_error( ):
    ''' Error results ignore transform. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    error = ValueError( 'test error' )
    result = generics.Error( error )
    transformed = result.transform( lambda x: x * 2 )
    assert transformed.is_error( )
    assert transformed is result


def test_300_result_abstract_methods( ):
    ''' Result abstract base class raises NotImplementedError. '''
    generics = cache_import_module( 'mimeogram.__.generics' )

    class ConcreteResult( generics.Result ): pass

    result = ConcreteResult( )
    with pytest.raises( NotImplementedError ):
        result.extract( )
    with pytest.raises( NotImplementedError ):
        result.transform( lambda x: x )


def test_400_result_match_args( ):
    ''' Result variants support pattern matching. '''
    generics = cache_import_module( 'mimeogram.__.generics' )
    value_result = generics.Value( 42 )
    error_result = generics.Error( ValueError( 'test' ) )
    # Value matching
    match value_result:
        case generics.Value( value ):
            assert value == 42
        case _:
            pytest.fail( 'Value pattern match failed' )
    # Error matching
    match error_result:
        case generics.Error( error ):
            assert isinstance( error, ValueError )
            assert str( error ) == 'test'
        case _:
            pytest.fail( 'Error pattern match failed' )
