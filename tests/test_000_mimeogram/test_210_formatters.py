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


''' Tests for formatters module. '''


import pytest
import re

from . import PACKAGE_NAME, cache_import_module


def _create_sample_part(
    location = 'test.txt',
    mimetype = 'text/plain',
    charset = 'utf-8',
    linesep = 'LF',
    content = 'Sample content'
):
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    return parts.Part(
        location = location,
        mimetype = mimetype,
        charset = charset,
        linesep = parts.LineSeparators[ linesep ],
        content = content
    )


def test_000_format_single_part( ):
    ''' Formatting a single part mimeogram. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create a sample part
    part = _create_sample_part()

    # Format the part
    mimeogram_text = formatters.format_mimeogram( [ part ] )

    # Validate the formatted text
    lines = mimeogram_text.split( '\n' )
    assert lines[ 0 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ 0 ].endswith( '====' )

    # Check for standard headers
    assert lines[ 1 ].startswith( 'Content-Location: test.txt' )
    assert lines[ 2 ].startswith(
        'Content-Type: text/plain; charset=utf-8; linesep=LF' )
    assert lines[ 4 ] == 'Sample content'

    # Check final boundary
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )

    # Optional: check that there are no extra lines
    assert len( lines ) == 6


def test_010_format_multiple_parts( ):
    ''' Formatting multiple parts in a mimeogram. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create multiple sample parts
    parts = [
        _create_sample_part(
            location = 'first.txt', content = 'First content' ),
        _create_sample_part(
            location = 'second.html',
            mimetype = 'text/html',
            content = '<html>Second content</html>'
        )
    ]

    # Format the parts
    mimeogram_text = formatters.format_mimeogram( parts )

    # Validate the formatted text
    boundary_pattern = r'--====MIMEOGRAM_[0-9a-f]{32}===='
    lines = mimeogram_text.split( '\n' )

    # Find boundaries
    boundary_indices = [
        i for i, line in enumerate( lines )
        if re.match( boundary_pattern, line )
    ]

    # Verify number of parts
    assert len( boundary_indices ) == 3, (
        "Expected three boundaries (including final)" )

    # Check first part
    assert lines[ boundary_indices[ 0 ] ].startswith( '--====MIMEOGRAM_' )
    assert lines[ boundary_indices[ 0 ] + 1 ].startswith(
        'Content-Location: first.txt' )
    assert lines[ boundary_indices[ 0 ] + 2 ].startswith(
        'Content-Type: text/plain; charset=utf-8; linesep=LF' )
    assert lines[ boundary_indices[ 0 ] + 4 ] == 'First content'

    # Check second part
    assert lines[ boundary_indices[ 1 ] + 1 ].startswith(
        'Content-Location: second.html' )
    assert 'Content-Type: text/html; charset=utf-8; linesep=LF' in (
        lines[ boundary_indices[ 1 ] + 2 ] )
    assert '<html>Second content</html>' in lines[ boundary_indices[ 1 ] + 4 ]

    # Check final boundary
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )


def test_020_format_with_message( ):
    ''' Formatting mimeogram with an introductory message. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create a sample part
    part = _create_sample_part()
    message = 'This is a test message for the mimeogram.'

    # Format with message
    mimeogram_text = formatters.format_mimeogram( [ part ], message = message )

    # Validate the formatted text
    lines = mimeogram_text.split( '\n' )

    # Check message part
    assert lines[ 0 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ 1 ] == 'Content-Location: mimeogram://message'
    assert lines[ 2 ].startswith(
        'Content-Type: text/plain; charset=utf-8; linesep=LF' )
    assert lines[ 4 ] == message

    # Check subsequent part
    assert 'Content-Location: test.txt' in '\n'.join( lines )

    # Verify final boundary
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )


def test_030_unicode_content( ):
    ''' Formatting mimeogram with Unicode content. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create a part with Unicode content
    part = _create_sample_part(
        location = 'unicode.txt',
        content = '你好世界 Hello World 🌍'
    )

    # Format the part
    mimeogram_text = formatters.format_mimeogram( [ part ] )

    # Validate the formatted text
    lines = mimeogram_text.split( '\n' )
    assert '你好世界 Hello World 🌍' in lines

    # Check boundary format remains consistent
    assert lines[ 0 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )


def test_040_part_with_unusual_characters( ):
    ''' Formatting part with unusual characters and escaping. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create a part with special characters
    part = _create_sample_part(
        location = 'special.txt',
        content = 'Line with\nline break\nand some "quotes"'
    )

    # Format the part
    mimeogram_text = formatters.format_mimeogram( [ part ] )

    # Validate the formatted text
    lines = mimeogram_text.split( '\n' )
    assert 'Line with' in lines
    assert 'line break' in lines
    assert 'and some "quotes"' in lines

    # Verify boundary integrity
    assert lines[ 0 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )


def test_050_empty_mimeogram_with_message( ):
    ''' Formatting a mimeogram with only a message. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    message = 'This is an important message.'

    # Format with message but no parts
    mimeogram_text = formatters.format_mimeogram( [], message = message )

    # Validate the formatted text
    lines = mimeogram_text.split( '\n' )
    assert lines[ 1 ] == 'Content-Location: mimeogram://message'
    assert lines[ 4 ] == message

    # Verify boundary format
    assert lines[ 0 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].startswith( '--====MIMEOGRAM_' )
    assert lines[ -1 ].endswith( '====--' )


def test_060_empty_mimeogram_without_message( ):
    ''' Attempt to format empty mimeogram without a message. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    with pytest.raises( exceptions.MimeogramFormatEmpty ):
        formatters.format_mimeogram( [] )


def test_070_verify_boundary_uniqueness( ):
    ''' Ensure unique boundary for each mimeogram. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )

    # Create two mimeograms
    parts = [ _create_sample_part() ]
    mimeogram1 = formatters.format_mimeogram( parts )
    mimeogram2 = formatters.format_mimeogram( parts )

    # Verify different boundaries
    boundary_pattern = r'--====MIMEOGRAM_([0-9a-f]{32})===='
    match1 = re.search( boundary_pattern, mimeogram1 )
    match2 = re.search( boundary_pattern, mimeogram2 )

    assert match1 is not None
    assert match2 is not None
    assert match1.group( 1 ) != match2.group( 1 )


def test_080_deterministic_boundary_basic( ):
    ''' Deterministic boundary produces reproducible output. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    part = _create_sample_part(
        location = 'deterministic.txt',
        content = 'Deterministic content'
    )
    mimeogram1 = formatters.format_mimeogram(
        [ part ], deterministic_boundary = True
    )
    mimeogram2 = formatters.format_mimeogram(
        [ part ], deterministic_boundary = True
    )
    assert mimeogram1 == mimeogram2
    boundary_pattern = r'--====MIMEOGRAM_([0-9a-f]{64})===='
    match = re.search( boundary_pattern, mimeogram1 )
    assert match is not None, 'Boundary should be a 64-character hex hash'


def test_090_deterministic_boundary_with_message( ):
    ''' Deterministic boundary works with message. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    part = _create_sample_part( content = 'Test content' )
    message = 'Test message'
    mimeogram1 = formatters.format_mimeogram(
        [ part ], message = message, deterministic_boundary = True
    )
    mimeogram2 = formatters.format_mimeogram(
        [ part ], message = message, deterministic_boundary = True
    )
    assert mimeogram1 == mimeogram2
    mimeogram3 = formatters.format_mimeogram(
        [ part ], message = 'Different message', deterministic_boundary = True
    )
    assert mimeogram1 != mimeogram3


def test_100_deterministic_boundary_different_content( ):
    ''' Deterministic boundary changes with different content. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    part1 = _create_sample_part( content = 'Content 1' )
    part2 = _create_sample_part( content = 'Content 2' )
    mimeogram1 = formatters.format_mimeogram(
        [ part1 ], deterministic_boundary = True
    )
    mimeogram2 = formatters.format_mimeogram(
        [ part2 ], deterministic_boundary = True
    )
    assert mimeogram1 != mimeogram2
    boundary_pattern = r'--====MIMEOGRAM_([0-9a-f]{64})===='
    match1 = re.search( boundary_pattern, mimeogram1 )
    match2 = re.search( boundary_pattern, mimeogram2 )
    assert match1 is not None
    assert match2 is not None
    assert match1.group( 1 ) != match2.group( 1 )


def test_110_deterministic_boundary_order_sensitivity( ):
    ''' Deterministic boundary is sensitive to part order. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    part1 = _create_sample_part( location = 'first.txt', content = 'First' )
    part2 = _create_sample_part( location = 'second.txt', content = 'Second' )
    mimeogram1 = formatters.format_mimeogram(
        [ part1, part2 ], deterministic_boundary = True
    )
    mimeogram2 = formatters.format_mimeogram(
        [ part2, part1 ], deterministic_boundary = True
    )
    assert mimeogram1 != mimeogram2


def test_120_deterministic_boundary_metadata_sensitivity( ):
    ''' Deterministic boundary is sensitive to part metadata. '''
    formatters = cache_import_module( f"{PACKAGE_NAME}.formatters" )
    part1 = _create_sample_part( mimetype = 'text/plain', content = 'Same' )
    part2 = _create_sample_part( mimetype = 'text/html', content = 'Same' )
    mimeogram1 = formatters.format_mimeogram(
        [ part1 ], deterministic_boundary = True
    )
    mimeogram2 = formatters.format_mimeogram(
        [ part2 ], deterministic_boundary = True
    )
    assert mimeogram1 != mimeogram2
