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


''' Tests for differences module. '''


from unittest.mock import patch

import pytest

from . import PACKAGE_NAME, cache_import_module, create_test_files


class MockDisplay:
    ''' Simple display implementation for testing. '''

    def __init__( self, context_lines: int = 3, inline_threshold: int = 24 ):
        self.context_lines = context_lines
        self.inline_threshold = inline_threshold
        self.displayed_lines: list[ str ] = [ ]

    async def __call__( self, lines: list[ str ] ) -> None:
        self.displayed_lines.extend( lines )


class AcceptInteractor:
    ''' Test interactor that always accepts changes. '''

    async def __call__( self, lines: list[ str ], display ):
        await display( lines )
        return True


class RejectInteractor:
    ''' Test interactor that always rejects changes. '''

    async def __call__( self, lines: list[ str ], display ):
        await display( lines )
        return False


@pytest.mark.asyncio
async def test_100_select_segments_empty_revision( provide_tempdir ):
    ''' Original content remains unchanged when revision matches. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    current = "test content"
    test_files = { "test.txt": current }
    test_path = provide_tempdir / "test.txt"

    with create_test_files( provide_tempdir, test_files ):
        part = parts.Part(
            location = str( test_path ),
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = parts.LineSeparators.LF,
            content = current )

        with patch( 'builtins.print' ):  # Silence "No changes" output
            revision = await differences.select_segments(
                part, test_path, current,
                display = MockDisplay( ),
                interactor = AcceptInteractor( ) )
            assert revision == current


@pytest.mark.asyncio
async def test_110_select_segments_with_changes( provide_tempdir ):
    ''' Change acceptance preserves modified content. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    current = "line 1\nline 2\nline 3"
    revision = "line 1\nmodified line\nline 3"
    test_files = { "test.txt": current }
    test_path = provide_tempdir / "test.txt"

    with create_test_files( provide_tempdir, test_files ):
        part = parts.Part(
            location = str( test_path ),
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = parts.LineSeparators.LF,
            content = current )

        display = MockDisplay( )
        result = await differences.select_segments(
            part, test_path, revision,
            display = display,
            interactor = AcceptInteractor( ) )
        assert result == revision
        assert any(
            line.startswith( '+modified line' )
            for line in display.displayed_lines )


@pytest.mark.asyncio
async def test_120_select_segments_reject_changes( provide_tempdir ):
    ''' Change rejection maintains original content. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    current = "line 1\nline 2\nline 3"
    revision = "line 1\nmodified line\nline 3"
    test_files = { "test.txt": current }
    test_path = provide_tempdir / "test.txt"

    with create_test_files( provide_tempdir, test_files ):
        part = parts.Part(
            location = str( test_path ),
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = parts.LineSeparators.LF,
            content = current )

        display = MockDisplay( )
        result = await differences.select_segments(
            part, test_path, revision,
            display = display,
            interactor = RejectInteractor( ) )
        assert result == current
        assert any(
            line.startswith( '+modified line' )
            for line in display.displayed_lines )


@pytest.mark.asyncio
async def test_130_select_segments_multiple_changes( # pylint: disable=too-many-locals
    provide_tempdir
):
    ''' Multiple changes handled correctly. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    current = "line 1\nline 2\nline 3\nline 4"
    revision = "modified 1\nline 2\nmodified 3\nline 4"
    test_files = { "test.txt": current }
    test_path = provide_tempdir / "test.txt"

    with create_test_files( provide_tempdir, test_files ):
        part = parts.Part(
            location = str( test_path ),
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = parts.LineSeparators.LF,
            content = current )

        display = MockDisplay( )
        result = await differences.select_segments(
            part, test_path, revision,
            display = display,
            interactor = AcceptInteractor( ) )
        assert result == revision
        displayed = '\n'.join( display.displayed_lines )
        assert '+modified 1' in displayed
        assert '+modified 3' in displayed


def test_200_format_segment( ):
    ''' Difference segments include proper context and markers. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )

    current_lines = [ "line 1", "line 2", "line 3", "line 4", "line 5" ]
    revision_lines = [
        "line 1", "modified line", "line 3", "line 4", "line 5" ]

    result = differences._format_segment(
        current_lines, revision_lines,
        i1 = 1, i2 = 2,  # Change at line 2
        j1 = 1, j2 = 2,
        context_lines = 2 )

    expected = [
        "@@ -2,1 +2,1 @@",
        " line 1",
        "-line 2",
        "+modified line",
        " line 3",
        " line 4",
    ]
    assert result == expected


def test_210_format_segment_at_start( ):
    ''' Changes at file start receive appropriate context. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )

    current_lines = [ "line 1", "line 2", "line 3" ]
    revision_lines = [ "modified line", "line 2", "line 3" ]

    result = differences._format_segment(
        current_lines, revision_lines,
        i1 = 0, i2 = 1,
        j1 = 0, j2 = 1,
        context_lines = 2 )

    expected = [
        "@@ -1,1 +1,1 @@",
        "-line 1",
        "+modified line",
        " line 2",
        " line 3",
    ]
    assert result == expected


def test_220_format_segment_at_end( ):
    ''' Changes at file end receive appropriate context. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )

    current_lines = [ "line 1", "line 2", "line 3" ]
    revision_lines = [ "line 1", "line 2", "modified line" ]

    result = differences._format_segment(
        current_lines, revision_lines,
        i1 = 2, i2 = 3,
        j1 = 2, j2 = 3,
        context_lines = 2 )

    expected = [
        "@@ -3,1 +3,1 @@",
        " line 1",
        " line 2",
        "-line 3",
        "+modified line",
    ]
    assert result == expected


@pytest.mark.asyncio
async def test_140_select_segments_handles_errors( provide_tempdir ):
    ''' Processing errors preserve original revision. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    current = "line 1\nline 2\nline 3"
    revision = "line 1\nmodified line\nline 3"
    test_files = { "test.txt": current }
    test_path = provide_tempdir / "test.txt"

    class ErrorDisplay:
        ''' Display that raises an error. '''
        context_lines = 3
        inline_threshold = 24
        async def __call__( self, lines ):
            raise RuntimeError( "Simulated error" )

    with create_test_files( provide_tempdir, test_files ):
        part = parts.Part(
            location = str( test_path ),
            mimetype = "text/plain",
            charset = "utf-8",
            linesep = parts.LineSeparators.LF,
            content = current )

        with patch( f"{PACKAGE_NAME}.differences._scribe.exception" ):
            result = await differences.select_segments(
                part, test_path, revision,
                display = ErrorDisplay( ),
                interactor = AcceptInteractor( ) )
            assert result == revision  # Original revision preserved


def test_230_format_segment_context_limits( ):
    ''' Context lines properly bounded by file limits. '''
    differences = cache_import_module( f"{PACKAGE_NAME}.differences" )

    current_lines = [ "line 1", "line 2" ]
    revision_lines = [ "modified 1", "modified 2" ]

    result = differences._format_segment(
        current_lines, revision_lines,
        i1 = 0, i2 = 2,
        j1 = 0, j2 = 2,
        context_lines = 5 )  # More context than file has

    expected = [
        "@@ -1,2 +1,2 @@",
        "-line 1",
        "-line 2",
        "+modified 1",
        "+modified 2",
    ]
    assert result == expected
