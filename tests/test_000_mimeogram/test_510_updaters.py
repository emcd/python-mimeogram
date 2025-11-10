# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
#
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


''' Tests for updaters module. '''


import sys

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import pytest

import accretive as accret
from exceptiongroup import ExceptionGroup

from . import (
    PACKAGE_NAME,
    cache_import_module,
    create_test_files,
)


@dataclass( frozen = True )
class _TestProtector:
    ''' Test implementation of protection verification with fixed status. '''
    active: bool = False
    reason: str | None = None

    def verify( self, path: Path ):
        fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )
        return fsprotect.Status(
            path = path,
            reason = self.reason and fsprotect.Reasons[ self.reason ],
            active = self.active
        )


@dataclass( frozen = True )
class _TestInteractor:
    ''' Test PartInteractor returning a configured resolution and content. '''
    resolution: str
    content: str

    async def __call__( self, target ):
        return self.resolution, self.content


@pytest.fixture
def provide_test_interactor( ):
    ''' Provides a default interactor that always applies an update. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    return _TestInteractor(
        resolution = parts.Resolutions.Apply,
        content = 'updated content'
    )


def produce_mock_auxdata( config = None ):
    ''' Creates a mock Globals object for testing. '''
    from contextlib import AsyncExitStack
    from platformdirs import PlatformDirs

    __ = cache_import_module( f"{PACKAGE_NAME}.__" )

    if config is None:
        config = { }

    return __.appcore.state.Globals(
        application = __.appcore.application.Information(
            name = 'mimeogram-test',
            version = '0.0.0'
        ),
        configuration = accret.Dictionary( config ),
        directories = PlatformDirs(
            appname = 'mimeogram-test',
            version = '0.0.0'
        ),
        distribution = __.appcore.distribution.Information(
            name = 'mimeogram-test',
            location = Path( ).resolve( ),
            editable = True
        ),
        exits = AsyncExitStack( )
    )


@pytest.mark.asyncio
async def test_100_update_simple_file(
    provide_tempdir, provide_test_interactor
):
    ''' Basic file update works correctly in Silent mode. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test.txt': 'original content' }
    with create_test_files( provide_tempdir, files ):
        test_part = parts.Part(
            location = 'test.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'updated content'
        )

        await updaters.update(
            produce_mock_auxdata( ),
            [ test_part ],
            mode = updaters.ReviewModes.Silent,
            base = provide_tempdir,
            protector = _TestProtector( active = False ),
            interactor = provide_test_interactor
        )

        updated = ( provide_tempdir / 'test.txt' ).read_text( )
        assert updated == 'updated content'


@pytest.mark.asyncio
async def test_110_update_skips_mimeogram_protocol(
    provide_tempdir, provide_test_interactor
):
    ''' Update should skip parts with mimeogram:// protocol. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    test_part = parts.Part(
        location = 'mimeogram://message',
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = detextive.LineSeparators.LF,
        content = 'test content'
    )

    await updaters.update(
        produce_mock_auxdata(),
        [ test_part ],
        mode = updaters.ReviewModes.Silent,
        base = provide_tempdir,
        protector = _TestProtector( active = False ),
        interactor = provide_test_interactor
    )

    assert not ( provide_tempdir / 'message' ).exists()


@pytest.mark.asyncio
async def test_120_update_respects_protection(
    provide_tempdir, provide_test_interactor
):
    ''' Update respects filesystem protections (active = True => skip). '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test.txt': 'original content' }
    with create_test_files( provide_tempdir, files ):
        test_part = parts.Part(
            location = 'test.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'updated content'
        )

        await updaters.update(
            produce_mock_auxdata(),
            [ test_part ],
            mode = updaters.ReviewModes.Silent,
            base = provide_tempdir,
            protector = _TestProtector(
                active = True, reason = 'CustomAddition' ),
            interactor = provide_test_interactor
        )

        updated = ( provide_tempdir / 'test.txt' ).read_text()
        assert updated == 'original content'


@pytest.mark.asyncio
async def test_130_update_override_protections(
    provide_tempdir, provide_test_interactor
):
    ''' Update can override protections if disable-protections=true. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test.txt': 'original content' }
    with create_test_files( provide_tempdir, files ):
        test_part = parts.Part(
            location = 'test.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'updated content'
        )

        await updaters.update(
            produce_mock_auxdata(
                {
                    'update-parts': {
                        'disable-protections': True
                    }
                }
            ),
            [ test_part ],
            mode = updaters.ReviewModes.Silent,
            base = provide_tempdir,
            protector = _TestProtector(
                active = True, reason = 'CustomAddition' ),
            interactor = provide_test_interactor
        )

        updated = ( provide_tempdir / 'test.txt' ).read_text()
        assert updated == 'updated content'


@pytest.mark.asyncio
async def test_140_update_respects_interactor( provide_tempdir ):
    ''' Update uses provided interactor for changes in Partitive mode. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test.txt': 'original content' }
    with create_test_files( provide_tempdir, files ):
        test_part = parts.Part(
            location = 'test.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'test content'
        )

        custom_interactor = _TestInteractor(
            resolution = parts.Resolutions.Apply,
            content = 'custom content'
        )

        await updaters.update(
            produce_mock_auxdata(),
            [ test_part ],
            mode = updaters.ReviewModes.Partitive,
            base = provide_tempdir,
            protector = _TestProtector( active = False ),
            interactor = custom_interactor
        )

        updated = ( provide_tempdir / 'test.txt' ).read_text()
        assert updated == 'custom content'


@pytest.mark.asyncio
async def test_150_atomic_update_handles_errors( provide_tempdir ):
    ''' Atomic update raises ContentUpdateFailure on write errors. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    test_path = provide_tempdir / 'test.txt'

    with patch( # noqa: SIM117
        'aiofiles.os.replace', side_effect = OSError( 'Test error' )
    ):
        with pytest.raises( exceptions.ContentUpdateFailure ):
            await updaters._update_content_atomic( test_path, 'test content' )


@pytest.mark.asyncio
async def test_160_partitive_ignore_mode( provide_tempdir ):
    ''' Partitive-mode Ignore action should not overwrite file. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test.txt': 'original content' }
    with create_test_files( provide_tempdir, files ):
        test_part = parts.Part(
            location = 'test.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'new content'
        )

        class IgnoreInteractor:
            async def __call__( self, target ):
                return parts.Resolutions.Ignore, target.part.content

        await updaters.update(
            produce_mock_auxdata(),
            [ test_part ],
            mode = updaters.ReviewModes.Partitive,
            base = provide_tempdir,
            protector = _TestProtector( active = False ),
            interactor = IgnoreInteractor( )
        )

        updated = ( provide_tempdir / 'test.txt' ).read_text()
        assert updated == 'original content'


@pytest.mark.skipif( 'win32' == sys.platform, reason = 'weirdness' )
@pytest.mark.asyncio
async def test_170_queue_and_reverter_rollback_on_error(
    provide_tempdir
):
    ''' Reverter restores files if error occurs on subsequent updates. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts_mod = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    files = {
        'file1.txt': 'file1 original',
        'file2.txt': 'file2 original'
    }
    with create_test_files( provide_tempdir, files ):
        part1 = parts_mod.Part(
            location = 'file1.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'file1 updated'
        )
        part2 = parts_mod.Part(
            location = 'file2.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.LF,
            content = 'file2 updated'
        )

        with patch( 'aiofiles.os.replace' ) as mock_replace:
            async def mock_replace_side_effect( src, dst ):
                if 'file2.txt' in dst:
                    raise OSError( 'Simulated write failure' )

            mock_replace.side_effect = mock_replace_side_effect

            auxdata = produce_mock_auxdata( )
            with pytest.raises( ExceptionGroup ) as eginfo:
                await updaters.update(
                    auxdata,
                    [ part1, part2 ],
                    mode = updaters.ReviewModes.Silent,
                    base = provide_tempdir
                )

            sub_exc = eginfo.value.exceptions[ 0 ]
            assert isinstance( sub_exc, exceptions.ContentUpdateFailure )
            assert 'file2.txt' in str( sub_exc )

        assert (
            ( provide_tempdir / 'file1.txt' ).read_text( )
            == 'file1 original' )
        assert (
            ( provide_tempdir / 'file2.txt' ).read_text( )
            == 'file2 original' )


@pytest.mark.asyncio
async def test_180_line_endings_preserved( provide_tempdir ):
    ''' CRLF line separators are preserved in the updated file. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    parts_mod = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    files = { 'test_windows.txt': 'line1\r\nline2\r\n' }
    with create_test_files( provide_tempdir, files ):
        part = parts_mod.Part(
            location = 'test_windows.txt',
            mimetype = 'text/plain',
            charset = 'utf-8',
            linesep = detextive.LineSeparators.CRLF,
            content = 'line1\r\nline2\r\nline3\r\n'
        )

        await updaters.update(
            produce_mock_auxdata( ),
            [ part ],
            mode = updaters.ReviewModes.Silent,
            base = provide_tempdir,
            protector = _TestProtector( active = False )
        )

        actual = ( provide_tempdir / 'test_windows.txt' ).read_bytes()
        assert actual == b'line1\r\nline2\r\nline3\r\n'


@pytest.mark.asyncio
async def test_190_reverter_direct_coverage( provide_tempdir ):
    ''' Direct Reverter calls for saving non-existent and existing files. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    detextive = cache_import_module( 'detextive' )
    parts_mod = cache_import_module( f"{PACKAGE_NAME}.parts" )

    reverter = updaters.Reverter( )

    nonexistent_path = provide_tempdir / 'nofile.txt'
    dummy_part = parts_mod.Part(
        location = str( nonexistent_path ),
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = detextive.LineSeparators.LF,
        content = ''
    )
    # 1) Non-existent => skip saving
    await reverter.save( dummy_part, nonexistent_path )
    assert nonexistent_path not in reverter.originals

    existing_path = provide_tempdir / 'existing.txt'
    existing_path.write_text( 'original content' )
    # 2) Existing => store original
    await reverter.save( dummy_part, existing_path )
    assert existing_path in reverter.originals
    assert reverter.originals[ existing_path ] == 'original content'

    # 3) Reverter.restore() uses self.revisions in reverse
    reverter.revisions.append( existing_path )

    newfile_path = provide_tempdir / 'newfile.txt'
    newfile_path.write_text( 'some new content' )
    reverter.revisions.append( newfile_path )

    await reverter.restore( )
    assert existing_path.read_text( ) == 'original content'
    assert not newfile_path.exists( )


@pytest.mark.skipif( 'win32' == sys.platform, reason = 'need to fix' )
def test_200_derive_location( ):
    ''' _derive_location handles filesystem locations and file:// URLs. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    result = updaters._derive_location( 'test.txt' )
    assert str( result ) == 'test.txt'

    result = updaters._derive_location( '/test/path.txt' )
    assert str( result ) == '/test/path.txt'

    result = updaters._derive_location( 'file:///test/path.txt' )
    assert str( result ) == '/test/path.txt'

    with pytest.raises( exceptions.LocationInvalidity ):
        updaters._derive_location( 'http://example.com/test.txt' )


def test_210_review_modes_completeness( ):
    ''' Ensures that Silent and Partitive are present in ReviewModes. '''
    updaters = cache_import_module( f"{PACKAGE_NAME}.updaters" )

    assert hasattr( updaters.ReviewModes, 'Silent' )
    assert hasattr( updaters.ReviewModes, 'Partitive' )
