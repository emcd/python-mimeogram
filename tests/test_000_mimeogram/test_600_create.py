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


''' Tests for create module. '''
# pylint: disable=too-many-locals


from unittest.mock import MagicMock

import pytest

from . import PACKAGE_NAME, cache_import_module, create_test_files


def verify_mimeogram_format(
    mimeogram: str, filepath: str, content: str,
    message: str | None = None
) -> None:
    ''' Verifies mimeogram structure using package parser. '''
    from mimeogram.parsers import parse

    parts = parse( mimeogram )

    if message is not None:
        assert len( parts ) == 2

        # First part should be message
        assert parts[ 0 ].location == 'mimeogram://message'
        assert parts[ 0 ].mimetype == 'text/plain'
        assert parts[ 0 ].charset == 'utf-8'
        assert message.strip( ) in parts[ 0 ].content

        # Second part should be content
        assert parts[ 1 ].location == filepath
        assert parts[ 1 ].mimetype == 'text/plain'
        assert parts[ 1 ].charset == 'utf-8'
        assert content.strip( ) in parts[ 1 ].content
    else:
        assert len( parts ) == 1
        assert parts[ 0 ].location == filepath
        assert parts[ 0 ].mimetype == 'text/plain'
        assert parts[ 0 ].charset == 'utf-8'
        assert content.strip( ) in parts[ 0 ].content


def test_100_command_default_values( ):
    ''' Command initializes with correct default values. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    cmd = create.Command( sources = [ 'test.txt' ] )
    assert cmd.clip is None
    assert cmd.edit is False
    assert cmd.prepend_prompt is False
    assert cmd.recurse is None
    assert cmd.strict is None


def test_110_command_configuration_edits( ):
    ''' Command generates correct configuration edits. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    # Test with clip enabled
    cmd = create.Command( sources = [ 'test.txt' ], clip = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'create', 'to-clipboard' )
    assert edits[ 0 ].value is True

    # Test with recursion enabled
    cmd = create.Command( sources = [ 'test.txt' ], recurse = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'acquire-parts', 'recurse-directories' )
    assert edits[ 0 ].value is True

    # Test with strict mode enabled
    cmd = create.Command( sources = [ 'test.txt' ], strict = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'acquire-parts', 'fail-on-invalid' )
    assert edits[ 0 ].value is True

    # Test with all options combined
    cmd = create.Command(
        sources = [ 'test.txt' ],
        clip = True,
        recurse = True,
        strict = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 3


@pytest.mark.asyncio
async def test_200_create_basic_file( provide_tempdir ):
    ''' Create handles basic file input correctly. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }
    printed_content = [ ]

    def mock_print( content: str ):
        printed_content.append( content )

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command( sources = [ str( test_path ) ] )
        with pytest.raises( SystemExit ) as exc_info:
            with pytest.MonkeyPatch( ).context( ) as mp:
                mp.setattr( 'builtins.print', mock_print )
                await create.create(
                    MagicMock( configuration = { } ),
                    cmd )

        assert exc_info.value.code == 0
        assert len( printed_content ) == 1
        verify_mimeogram_format(
            printed_content[0], str(test_path), test_content )


@pytest.mark.asyncio
async def test_210_create_with_message( provide_tempdir ):
    ''' Create includes edited message when requested. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }
    test_message = "Test message\n"
    printed_content = [ ]

    def mock_print( content: str ):
        printed_content.append( content )

    async def test_editor( ) -> str:
        return test_message

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( test_path ) ],
            edit = True )
        with pytest.raises( SystemExit ) as exc_info:
            with pytest.MonkeyPatch( ).context( ) as mp:
                mp.setattr( 'builtins.print', mock_print )
                await create.create(
                    MagicMock( configuration = { } ),
                    cmd,
                    editor = test_editor )

        assert exc_info.value.code == 0
        assert len( printed_content ) == 1
        output = printed_content[ 0 ]
        verify_mimeogram_format(
            output,
            str(test_path),
            test_content,
            message=test_message )


@pytest.mark.asyncio
async def test_220_create_with_prompt( provide_tempdir ):
    ''' Create prepends format instructions when requested. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }
    test_prompt = "Test prompt\n"
    printed_content = [ ]

    def mock_print( content: str ):
        printed_content.append( content )

    async def test_prompter( auxdata ): # pylint: disable=unused-argument
        return test_prompt

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( test_path ) ],
            prepend_prompt = True )
        with pytest.raises( SystemExit ) as exc_info:
            with pytest.MonkeyPatch( ).context( ) as mp:
                mp.setattr( 'builtins.print', mock_print )
                await create.create(
                    MagicMock( configuration = { } ),
                    cmd,
                    prompter = test_prompter )

        assert exc_info.value.code == 0
        assert len( printed_content ) == 1
        output = printed_content[ 0 ]
        verify_mimeogram_format( output, str(test_path), test_content )
        assert test_prompt.strip( ) in output


@pytest.mark.asyncio
async def test_230_create_to_clipboard( provide_tempdir ):
    ''' Create copies output to clipboard when requested. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }
    copied_content = None

    async def test_clipcopier( content: str ) -> None:
        nonlocal copied_content
        copied_content = content

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( test_path ) ],
            clip = True )
        with pytest.raises( SystemExit ) as exc_info:
            await create.create(
                MagicMock(
                    configuration = { 'create': { 'to-clipboard': True } } ),
                cmd,
                clipcopier = test_clipcopier )

        assert exc_info.value.code == 0
        assert copied_content is not None
        verify_mimeogram_format( copied_content, str(test_path), test_content )


@pytest.mark.asyncio
async def test_240_create_with_recursion( provide_tempdir ):
    ''' Create handles directory recursion correctly. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_files = {
        "dir1/file1.txt": "content1\n",
        "dir1/subdir/file2.txt": "content2\n",
        "dir2/file3.txt": "content3\n"
    }
    printed_content = [ ]

    def mock_print( content: str ):
        printed_content.append( content )

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( provide_tempdir ) ],
            recurse = True )
        with pytest.raises( SystemExit ) as exc_info:
            with pytest.MonkeyPatch( ).context( ) as mp:
                mp.setattr( 'builtins.print', mock_print )
                await create.create(
                    MagicMock(
                        configuration = {
                            'acquire-parts': { 'recurse-directories': True }
                        } ),
                    cmd )

        assert exc_info.value.code == 0
        assert len( printed_content ) == 1
        output = printed_content[ 0 ]
        # Verify all paths and content exist in output
        for path, content in test_files.items():
            test_path = provide_tempdir / path
            assert str(test_path) in output
            assert content.strip() in output


@pytest.mark.asyncio
async def test_250_create_acquisition_failure( provide_tempdir ):
    ''' Create handles part acquisition failures appropriately. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    nonexistent_path = provide_tempdir / "nonexistent.txt"
    cmd = create.Command( sources = [ str( nonexistent_path ) ] )

    with pytest.raises( SystemExit ) as exc_info:
        await create.create( MagicMock( configuration = { } ), cmd )

    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_300_create_message_edit_failure( provide_tempdir ):
    ''' Create handles message editing failures appropriately. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }

    async def failing_editor( ) -> str:
        raise RuntimeError( "Edit error" )

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( test_path ) ],
            edit = True )
        with pytest.raises( SystemExit ) as exc_info:
            await create.create(
                MagicMock( configuration = { } ),
                cmd,
                editor = failing_editor )

        assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_310_create_clipboard_failure( provide_tempdir ):
    ''' Create handles clipboard failures appropriately. '''
    create = cache_import_module( f"{PACKAGE_NAME}.create" )

    test_content = "test content\n"
    test_path = provide_tempdir / "test.txt"
    test_files = { "test.txt": test_content }

    async def failing_clipcopier( content: str ) -> None:
        raise RuntimeError( "Clipboard error" )

    with create_test_files( provide_tempdir, test_files ):
        cmd = create.Command(
            sources = [ str( test_path ) ],
            clip = True )
        with pytest.raises( SystemExit ) as exc_info:
            await create.create(
                MagicMock(
                    configuration = { 'create': { 'to-clipboard': True } } ),
                cmd,
                clipcopier = failing_clipcopier )

        assert exc_info.value.code == 1
