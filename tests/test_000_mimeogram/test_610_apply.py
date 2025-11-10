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


''' Tests for apply module. '''


import types

import pytest

from . import PACKAGE_NAME, cache_import_module


@pytest.mark.usefixtures( )
class MockContentAcquirer:
    ''' Test implementation of content acquisition. '''

    def __init__(
        self,
        *,
        stdin_is_terminal: bool = True,
        stdin_content: str = '',
        clipboard_content: str = '',
        file_contents: dict[ str, str ] | None = None,
    ):
        self._stdin_is_terminal = stdin_is_terminal
        self._stdin_content = stdin_content
        self._clipboard_content = clipboard_content
        self._file_contents = file_contents or {}

    def stdin_is_tty( self ) -> bool:
        return self._stdin_is_terminal

    async def acquire_clipboard( self ) -> str:
        return self._clipboard_content

    async def acquire_file( self, path: str | None ) -> str:
        if path in self._file_contents:
            return self._file_contents[ path ]
        raise FileNotFoundError( f"File not found: {path}" )

    async def acquire_stdin( self ) -> str:
        return self._stdin_content


def test_100_command_default_values( ):
    ''' Command initializes with correct default values. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    cmd = apply.Command( )
    assert cmd.source == '-'
    assert cmd.clip is None
    assert cmd.mode is None
    assert cmd.base is None
    assert cmd.force is None


def test_110_command_configuration_edits( ):
    ''' Command generates correct configuration edits. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    # Test with clip enabled
    cmd = apply.Command( clip = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'apply', 'from-clipboard' )
    assert edits[ 0 ].value is True

    # Test with force enabled
    cmd = apply.Command( force = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'update-parts', 'disable-protections' )
    assert edits[ 0 ].value is True

    # Test with both options
    cmd = apply.Command( clip = True, force = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 2


@pytest.mark.asyncio
async def test_200_acquire_from_stdin( ):
    ''' _acquire reads content from stdin when source is "-". '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    test_content = "test mimeogram content"
    cmd = apply.Command( source = '-' )
    acquirer = MockContentAcquirer( stdin_content = test_content )

    content = await apply._acquire(
        types.SimpleNamespace( configuration = { } ),
        cmd,
        acquirer )
    assert content == test_content


@pytest.mark.asyncio
async def test_210_acquire_from_file( ):
    ''' _acquire reads content from specified file. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    test_content = "test mimeogram content"
    test_file = "test.mg"
    cmd = apply.Command( source = test_file )
    acquirer = MockContentAcquirer(
        file_contents = { test_file: test_content } )

    content = await apply._acquire(
        types.SimpleNamespace( configuration = { } ),
        cmd,
        acquirer )
    assert content == test_content


@pytest.mark.asyncio
async def test_220_acquire_from_clipboard( ):
    ''' _acquire reads content from clipboard when configured. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    test_content = "test mimeogram content"
    cmd = apply.Command( )
    auxdata = types.SimpleNamespace(
        configuration = { 'apply': { 'from-clipboard': True } } )
    acquirer = MockContentAcquirer( clipboard_content = test_content )

    content = await apply._acquire( auxdata, cmd, acquirer )
    assert content == test_content


@pytest.mark.asyncio
async def test_230_acquire_empty_clipboard( ):
    ''' _acquire handles empty clipboard appropriately. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    cmd = apply.Command( )
    auxdata = types.SimpleNamespace(
        configuration = { 'apply': { 'from-clipboard': True } } )
    acquirer = MockContentAcquirer( clipboard_content = '' )

    with pytest.raises( SystemExit ) as exc_info:
        await apply._acquire( auxdata, cmd, acquirer )
    assert exc_info.value.code == 1


def test_300_determine_review_mode_tty( ):
    ''' _determine_review_mode selects correct mode for TTY. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )

    acquirer = MockContentAcquirer( stdin_is_terminal = True )

    # No mode specified
    cmd = apply.Command( )
    assert (apply._determine_review_mode( cmd, acquirer )
            is updaters.ReviewModes.Partitive)

    # Explicit mode
    cmd = apply.Command( mode = updaters.ReviewModes.Silent )
    assert (apply._determine_review_mode( cmd, acquirer )
            is updaters.ReviewModes.Silent)


def test_310_determine_review_mode_non_tty( ):
    ''' _determine_review_mode handles non-TTY appropriately. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )

    acquirer = MockContentAcquirer( stdin_is_terminal = False )

    # No mode specified
    cmd = apply.Command( )
    assert (apply._determine_review_mode( cmd, acquirer )
            is updaters.ReviewModes.Silent)

    # Interactive mode requested - should fail
    cmd = apply.Command( mode = updaters.ReviewModes.Partitive )
    with pytest.raises( SystemExit ) as exc_info:
        apply._determine_review_mode( cmd, acquirer )
    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_400_apply_success( ):
    ''' apply function handles successful case correctly. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    test_content = "test mimeogram"
    test_parts = [
        parts.Part(
            location = "test.txt",
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = detextive.LineSeparators.LF,
            content = "test content" ) ]

    async def mock_updater(
        auxdata, parts, mode, *, base = None
    ) -> None:
        pass  # Successful update

    def mock_parser( content: str ):
        return test_parts

    acquirer = MockContentAcquirer( stdin_content = test_content )

    with pytest.raises( SystemExit ) as exc_info:
        cmd = apply.Command( )
        await apply.apply(
            types.SimpleNamespace( configuration = { } ),
            cmd,
            acquirer = acquirer,
            parser = mock_parser,
            updater = mock_updater )

    assert exc_info.value.code == 0


@pytest.mark.asyncio
async def test_410_apply_empty_content( ):
    ''' apply function handles empty content appropriately. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    acquirer = MockContentAcquirer( stdin_content = '' )

    with pytest.raises( SystemExit ) as exc_info:
        cmd = apply.Command( )
        await apply.apply(
            types.SimpleNamespace( configuration = { } ),
            cmd,
            acquirer = acquirer )

    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_420_apply_parse_failure( ):
    ''' apply function handles parse failures appropriately. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )

    def failing_parser( content: str ):
        raise ValueError( "Parse error" )

    acquirer = MockContentAcquirer( stdin_content = "invalid content" )

    with pytest.raises( SystemExit ) as exc_info:
        cmd = apply.Command( )
        await apply.apply(
            types.SimpleNamespace( configuration = { } ),
            cmd,
            acquirer = acquirer,
            parser = failing_parser )

    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_430_apply_update_failure( ):
    ''' apply function handles update failures appropriately. '''
    apply = cache_import_module( f"{PACKAGE_NAME}.apply" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    test_content = "test mimeogram"
    test_parts = [
        parts.Part(
            location = "test.txt",
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = detextive.LineSeparators.LF,
            content = "test content" ) ]

    async def failing_updater( auxdata, parts, **kwargs ):
        raise ValueError( "Update error" )

    def mock_parser( content: str ):
        return test_parts

    acquirer = MockContentAcquirer( stdin_content = test_content )

    with pytest.raises( SystemExit ) as exc_info:
        cmd = apply.Command( )
        await apply.apply(
            types.SimpleNamespace( configuration = { } ),
            cmd,
            acquirer = acquirer,
            parser = mock_parser,
            updater = failing_updater )

    assert exc_info.value.code == 1
