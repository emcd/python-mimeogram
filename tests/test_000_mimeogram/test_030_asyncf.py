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


''' Tests for asyncf module. '''


import pytest

from exceptiongroup import ExceptionGroup

from . import cache_import_module


@pytest.mark.asyncio
async def test_000_gather_async_success( ):
    ''' gather_async collects successful results. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def success1( ): return 1
    async def success2( ): return 2

    results = await asyncf.gather_async( success1( ), success2( ) )
    assert results == ( 1, 2 )


@pytest.mark.asyncio
async def test_010_gather_async_error_handling( ):
    ''' gather_async handles errors appropriately. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def success( ): return 42
    async def failure( ): raise ValueError( 'test error' )

    with pytest.raises( ExceptionGroup ) as exc_info:
        await asyncf.gather_async( success( ), failure( ) )
    assert len( exc_info.value.exceptions ) == 1
    assert isinstance( exc_info.value.exceptions[ 0 ], ValueError )
    results = await asyncf.gather_async(
        success( ), failure( ), return_exceptions = True )
    assert len( results ) == 2
    assert results[ 0 ].extract( ) == 42
    assert isinstance( results[ 1 ].error, ValueError )


@pytest.mark.asyncio
async def test_020_gather_async_nonawaitables( ):
    ''' gather_async handles non-awaitable operands. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def success( ): return 42

    nonawaitable = 'not coroutine'
    with pytest.raises( TypeError ):
        await asyncf.gather_async( success( ), nonawaitable )
    results = await asyncf.gather_async(
        success( ), nonawaitable,
        ignore_nonawaitables = True, return_exceptions = True )
    assert len( results ) == 2
    assert results[ 0 ].is_value( )
    assert results[ 0 ].extract( ) == 42
    assert results[ 1 ].is_value( )
    assert results[ 1 ].extract( ) == 'not coroutine'


@pytest.mark.asyncio
async def test_030_gather_async_error_message( ):
    ''' gather_async uses custom error message. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def failure( ): raise ValueError( 'test error' )

    message = 'Custom error message'
    with pytest.raises( ExceptionGroup ) as exc_info:
        await asyncf.gather_async( failure( ), error_message = message )
    assert str( exc_info.value ).startswith( message )


@pytest.mark.asyncio
async def test_100_intercept_error_success( ):
    ''' intercept_error_async wraps successful results. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def success( ): return 42

    result = await asyncf.intercept_error_async( success( ) )
    assert result.is_value( )
    assert result.extract( ) == 42


@pytest.mark.asyncio
async def test_110_intercept_error_failure( ):
    ''' intercept_error_async wraps errors. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def failure( ): raise ValueError( 'test error' )

    result = await asyncf.intercept_error_async( failure( ) )
    assert result.is_error( )
    assert isinstance( result.error, ValueError )


@pytest.mark.asyncio
async def test_120_intercept_error_system( ):
    ''' intercept_error_async propagates system errors. '''
    asyncf = cache_import_module( 'mimeogram.__.asyncf' )

    async def system_error( ): raise KeyboardInterrupt( )

    with pytest.raises( KeyboardInterrupt ):
        await asyncf.intercept_error_async( system_error( ) )
