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


''' Tests for io module. '''


from exceptiongroup import ExceptionGroup

import pytest

from . import cache_import_module, create_test_files


@pytest.mark.asyncio
async def test_000_acquire_text_file_async( provide_tempdir ):
    ''' acquire_text_file_async reads file content. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_content = 'test content\nline 2'
    test_files = { 'test.txt': test_content }
    with create_test_files( provide_tempdir, test_files ):
        content = await io.acquire_text_file_async(
            provide_tempdir / 'test.txt' )
        assert content == test_content


@pytest.mark.asyncio
async def test_010_acquire_text_file_async_with_deserializer(
    provide_tempdir
):
    ''' acquire_text_file_async uses deserializer when provided. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_content = '{"key": "value"}'
    test_files = { 'test.json': test_content }

    def deserialize( text ):
        return { 'deserialized': text }

    with create_test_files( provide_tempdir, test_files ):
        content = await io.acquire_text_file_async(
            provide_tempdir / 'test.json',
            deserializer = deserialize )
        assert content == { 'deserialized': test_content }


@pytest.mark.asyncio
async def test_020_acquire_text_file_async_error( provide_tempdir ):
    ''' acquire_text_file_async handles file errors. '''
    io = cache_import_module( 'mimeogram.__.io' )
    with pytest.raises( FileNotFoundError ):
        await io.acquire_text_file_async( provide_tempdir / 'nonexistent.txt' )


@pytest.mark.asyncio
async def test_100_acquire_text_files_async( provide_tempdir ):
    ''' acquire_text_files_async reads multiple files. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_files = {
        'file1.txt': 'content1',
        'file2.txt': 'content2',
    }
    with create_test_files( provide_tempdir, test_files ):
        contents = await io.acquire_text_files_async(
            provide_tempdir / 'file1.txt',
            provide_tempdir / 'file2.txt' )
        assert contents == ( 'content1', 'content2' )


@pytest.mark.asyncio
async def test_110_acquire_text_files_async_with_errors( provide_tempdir ):
    ''' acquire_text_files_async handles file errors. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_files = { 'file1.txt': 'content1' }
    with create_test_files( provide_tempdir, test_files ):
        with pytest.raises( ExceptionGroup ) as exc_info:
            await io.acquire_text_files_async(
                provide_tempdir / 'file1.txt',
                provide_tempdir / 'nonexistent.txt' )
        assert len( exc_info.value.exceptions ) == 1
        assert isinstance( exc_info.value.exceptions[ 0 ], FileNotFoundError )
        results = await io.acquire_text_files_async(
            provide_tempdir / 'file1.txt',
            provide_tempdir / 'nonexistent.txt',
            return_exceptions = True )
        assert results[ 0 ].is_value( )
        assert results[ 0 ].extract( ) == 'content1'
        assert results[ 1 ].is_error( )
        assert isinstance( results[ 1 ].error, FileNotFoundError )


@pytest.mark.asyncio
async def test_120_acquire_text_files_async_with_deserializer(
    provide_tempdir
):
    ''' acquire_text_files_async applies deserializer to all files. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_files = {
        'file1.txt': 'content1',
        'file2.txt': 'content2',
    }

    def deserialize( text ):
        return f"deserialized_{text}"

    with create_test_files( provide_tempdir, test_files ):
        contents = await io.acquire_text_files_async(
            provide_tempdir / 'file1.txt',
            provide_tempdir / 'file2.txt',
            deserializer = deserialize )
        assert contents == ( 'deserialized_content1', 'deserialized_content2' )


@pytest.mark.asyncio
async def test_130_acquire_text_files_async_deserializer_with_errors(
    provide_tempdir
):
    ''' acquire_text_files_async handles deserializer errors. '''
    io = cache_import_module( 'mimeogram.__.io' )
    test_files = {
        'file1.txt': 'content1',
        'file2.txt': 'content2',
    }

    def failing_deserializer( text ):
        if 'content2' in text:
            raise ValueError( 'Deserialize error' )
        return f"deserialized_{text}"

    with create_test_files( provide_tempdir, test_files ):
        with pytest.raises( ExceptionGroup ) as exc_info:
            await io.acquire_text_files_async(
                provide_tempdir / 'file1.txt',
                provide_tempdir / 'file2.txt',
                deserializer = failing_deserializer )
        assert len( exc_info.value.exceptions ) == 1
        assert isinstance( exc_info.value.exceptions[ 0 ], ValueError )
        results = await io.acquire_text_files_async(
            provide_tempdir / 'file1.txt',
            provide_tempdir / 'file2.txt',
            deserializer = failing_deserializer,
            return_exceptions = True )
        assert results[ 0 ].is_value( )
        assert results[ 0 ].extract( ) == 'deserialized_content1'
        assert results[ 1 ].is_error( )
        assert isinstance( results[ 1 ].error, ValueError )
