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


''' Tests for parsers module. '''


import pytest

from . import PACKAGE_NAME, cache_import_module

__ = cache_import_module( f"{PACKAGE_NAME}.__" )
LineSeparators = __.detextive.LineSeparators


def _create_sample_mimeogram(
    location = 'test.txt',
    mimetype = 'text/plain',
    charset = 'utf-8',
    linesep = 'LF',
    content = 'Sample content',
    boundary = '====MIMEOGRAM_0123456789abcdef===='
):
    return (
        f"--{boundary}\n"
        f"Content-Location: {location}\n"
        f"Content-Type: {mimetype}; charset={charset}; linesep={linesep}\n"
        "\n"
        f"{content}\n"
        f"--{boundary}--\n"
    )


def test_000_basic_parse( ):
    ''' Simple valid mimeogram. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    # Create a simple test mimeogram
    mimeogram_text = _create_sample_mimeogram()
    parsed_parts = parsers.parse( mimeogram_text )

    assert len( parsed_parts ) > 0, "Parsing should return at least one part"

    # Check first part's attributes
    first_part = parsed_parts[ 0 ]
    assert isinstance( first_part, parts.Part )
    assert first_part.location == 'test.txt'
    assert first_part.mimetype == 'text/plain'
    assert first_part.charset == 'utf-8'
    assert first_part.linesep == LineSeparators.LF
    assert first_part.content == 'Sample content'


def test_010_parse_multiple_parts( ):
    ''' Mimeogram with multiple parts. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Create mimeogram with multiple parts
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: first.txt\n"
        "Content-Type: text/plain; charset=utf-8; linesep=LF\n"
        "\n"
        "First content\n"
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: second.txt\n"
        "Content-Type: text/html; charset=utf-8; linesep=LF\n"
        "\n"
        "<html>Second content</html>\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )
    parsed_parts = parsers.parse( mimeogram_text )

    assert len( parsed_parts ) == 2, "Parsing should return multiple parts"
    assert parsed_parts[ 0 ].location == 'first.txt'
    assert parsed_parts[ 0 ].content == 'First content'
    assert parsed_parts[ 1 ].location == 'second.txt'
    assert parsed_parts[ 1 ].content == '<html>Second content</html>'


def test_020_parse_part_details( ):
    ''' Details of a single part. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )
    # Create mimeogram with detailed headers
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: detailed.txt\n"
        "Content-Type: application/json; charset=utf-8; linesep=CRLF\n"
        "X-Extra-Header: test\n"
        "\n"
        '{"key": "value"}\r\n'
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )
    parsed_parts = parsers.parse( mimeogram_text )

    first_part = parsed_parts[ 0 ]
    assert first_part.location == 'detailed.txt'
    assert first_part.mimetype == 'application/json'
    assert first_part.charset == 'utf-8'
    assert first_part.linesep == LineSeparators.CRLF
    assert first_part.content == '{"key": "value"}'


def test_030_empty_mimeogram_parse( ):
    ''' An empty mimeogram raises an exception. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    with pytest.raises( exceptions.MimeogramParseFailure ):
        parsers.parse( '' )


def test_040_malformed_boundary( ):
    ''' Mimeogram with malformed boundary. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    # Mimeogram with an invalid boundary (fewer than 16 hex digits)
    with pytest.raises( exceptions.MimeogramParseFailure ):
        mimeogram_text = (
            "--INVALID_BOUNDARY===\n"
            "Content-Location: test.txt\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Content\n"
            "--INVALID_BOUNDARY===--\n"
        )
        parsers.parse( mimeogram_text )


def test_050_no_parts_found( ):
    ''' Mimeogram with no valid parts. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Create a mimeogram without valid parts
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )

    parsed_parts = parsers.parse( mimeogram_text )
    assert len( parsed_parts ) == 0, "Expected an empty list of parts"


def test_060_non_standard_headers( ):
    ''' Mimeogram with non-standard but valid headers. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Test mimeogram with case-insensitive and extra headers
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "content-location: test.txt\n"
        "CONTENT-TYPE: text/plain; charset=UTF-8; linesep=LF\n"
        "X-Extra-Header: ignored\n"
        "\n"
        "Content\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )

    parsed_parts = parsers.parse( mimeogram_text )
    assert len( parsed_parts ) == 1


def test_070_unicode_content( ):
    ''' Mimeogram with Unicode content. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Mimeogram with Unicode content
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: unicode.txt\n"
        "Content-Type: text/plain; charset=utf-8; linesep=LF\n"
        "\n"
        "你好世界 Hello World 🌍\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )
    parsed_parts = parsers.parse( mimeogram_text )

    assert len( parsed_parts ) > 0
    # Assert that some parts contain non-ASCII characters
    assert any(
        any( ord(char) > 127 for char in part.content )
        for part in parsed_parts
    )
    assert parsed_parts[ 0 ].content == '你好世界 Hello World 🌍'


def test_080_line_separator_variations( ):
    ''' Mimeograms with different line separators. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )
    # Create test cases for LF and CRLF line separators
    separators = [
        ('\n', LineSeparators.LF),
        ('\r\n', LineSeparators.CRLF)
    ]

    for sep, expected_type in separators:
        mimeogram_text = (
            f"--====MIMEOGRAM_0123456789abcdef===={sep}"
            f"Content-Location: test.txt{sep}"
            f"Content-Type: text/plain; charset=utf-8; "
            f"linesep={expected_type.name}{sep}"
            f"{sep}"
            f"Content{sep}"
            f"--====MIMEOGRAM_0123456789abcdef====--{sep}"
        )

        parsed_parts = parsers.parse( mimeogram_text )
        assert len( parsed_parts ) == 1
        assert parsed_parts[ 0 ].linesep == expected_type
        assert parsed_parts[ 0 ].content == 'Content'


def test_090_trailing_text( ):
    ''' Mimeogram with trailing text after final boundary. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Create mimeogram with trailing text
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: test.txt\n"
        "Content-Type: text/plain; charset=utf-8; linesep=LF\n"
        "\n"
        "Content\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
        "Some trailing text"
    )

    parsed_parts = parsers.parse( mimeogram_text )
    assert len( parsed_parts ) == 1
    assert parsed_parts[ 0 ].content == 'Content'


def test_100_missing_final_boundary( ):
    ''' Mimeogram without a final boundary. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Mimeogram without final boundary
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: first.txt\n"
        "Content-Type: text/plain; charset=utf-8; linesep=LF\n"
        "\n"
        "First content\n"
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: second.txt\n"
        "Content-Type: text/html; charset=utf-8; linesep=LF\n"
        "\n"
        "<html>Second content</html>\n"
    )

    parsed_parts = parsers.parse( mimeogram_text )
    assert len( parsed_parts ) == 2
    assert parsed_parts[ 0 ].location == 'first.txt'
    assert parsed_parts[ 0 ].content == 'First content'
    assert parsed_parts[ 1 ].location == 'second.txt'
    assert parsed_parts[ 1 ].content == '<html>Second content</html>'


def test_110_no_empty_line_between_headers( ):
    ''' Mimeogram without an empty line between headers and content. '''
    parsers = cache_import_module( f"{PACKAGE_NAME}.parsers" )

    # Mimeogram without empty line between headers and content
    mimeogram_text = (
        "--====MIMEOGRAM_0123456789abcdef====\n"
        "Content-Location: test.txt\n"
        "Content-Type: text/plain; charset=utf-8; linesep=LF\n"
        "Content\n"
        "--====MIMEOGRAM_0123456789abcdef====--\n"
    )

    parsed_parts = parsers.parse( mimeogram_text )
    assert len( parsed_parts ) == 1
    assert parsed_parts[ 0 ].location == 'test.txt'
    assert parsed_parts[ 0 ].content == 'Content'
