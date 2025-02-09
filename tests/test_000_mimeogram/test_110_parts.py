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


''' Tests for parts module. '''


from . import PACKAGE_NAME, cache_import_module


def test_000_line_separators_enum( ):
    ''' Line separator enum values and attributes. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    # Check enum values
    assert parts.LineSeparators.CR.value == '\r'
    assert parts.LineSeparators.CRLF.value == '\r\n'
    assert parts.LineSeparators.LF.value == '\n'


def test_010_line_separators_detection( ):
    ''' Line separator detection from bytes. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    # Test detection of different line separators
    cr_bytes = b'line1\rline2\rline3'
    crlf_bytes = b'line1\r\nline2\r\nline3'
    lf_bytes = b'line1\nline2\nline3'
    mixed_bytes = b'line1\rline2\nline3\r\n'
    double_cr_bytes = b'line1\r\rline2\r\rline3'
    empty_bytes = b''
    no_terminator_bytes = b'line1line2line3'

    assert (
        parts.LineSeparators.detect_bytes( cr_bytes )
        == parts.LineSeparators.CR )
    assert (
        parts.LineSeparators.detect_bytes( crlf_bytes )
        == parts.LineSeparators.CRLF )
    assert (
        parts.LineSeparators.detect_bytes( lf_bytes )
        == parts.LineSeparators.LF )

    # With mixed bytes, it detects the first encountered line separator
    assert (
        parts.LineSeparators.detect_bytes( mixed_bytes )
        == parts.LineSeparators.CR )

    # Double CR case
    assert (
        parts.LineSeparators.detect_bytes( double_cr_bytes )
        == parts.LineSeparators.CR )

    # Empty bytes and bytes without terminators
    assert parts.LineSeparators.detect_bytes( empty_bytes ) is None
    assert parts.LineSeparators.detect_bytes( no_terminator_bytes ) is None


def test_020_line_separators_normalization( ):
    ''' Line separator normalization methods. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    # Test universal normalization
    mixed_content = "line1\rline2\r\nline3\n"
    normalized = parts.LineSeparators.normalize_universal( mixed_content )
    assert normalized == "line1\nline2\nline3\n"

    # Test specific separator nativization and normalization
    cr_content = "line1\rline2\rline3"
    lf_sep = parts.LineSeparators.LF
    cr_sep = parts.LineSeparators.CR
    crlf_sep = parts.LineSeparators.CRLF

    # Test LF nativization (no change)
    assert lf_sep.nativize( cr_content ) == cr_content
    assert lf_sep.normalize( cr_content ) == cr_content

    # Test CR nativization
    assert cr_sep.nativize( cr_content.replace('\r', '\n') ) == cr_content
    assert cr_sep.normalize( cr_content ) == cr_content.replace('\r', '\n')

    # Test CRLF nativization
    crlf_content = cr_content.replace('\r', '\r\n')
    assert crlf_sep.nativize( cr_content.replace('\r', '\n') ) == crlf_content
    assert crlf_sep.normalize( crlf_content ) == cr_content.replace('\r', '\n')


def test_100_part_immutability( ):
    ''' Part class immutability. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    import dataclasses
    import pytest

    # Create a Part instance
    part = parts.Part(
        location = 'test.txt',
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = parts.LineSeparators.LF,
        content = 'test content'
    )

    # Verify immutability through dataclass
    with pytest.raises( dataclasses.FrozenInstanceError ):
        part.location = 'new.txt'
    with pytest.raises( dataclasses.FrozenInstanceError ):
        part.mimetype = 'application/json'
    with pytest.raises( dataclasses.FrozenInstanceError ):
        part.charset = 'ascii'
    with pytest.raises( dataclasses.FrozenInstanceError ):
        part.linesep = parts.LineSeparators.CRLF
    with pytest.raises( dataclasses.FrozenInstanceError ):
        part.content = 'new content'


def test_110_part_creation( ):
    ''' Creating Part instances with different parameters. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    # Test with various valid inputs
    part_1 = parts.Part(
        location = '/path/to/file.txt',
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = parts.LineSeparators.LF,
        content = 'Sample text content'
    )

    # Verify all attributes are set correctly
    assert part_1.location == '/path/to/file.txt'
    assert part_1.mimetype == 'text/plain'
    assert part_1.charset == 'utf-8'
    assert part_1.linesep == parts.LineSeparators.LF
    assert part_1.content == 'Sample text content'

    # Test with URL location
    part_2 = parts.Part(
        location = 'https://example.com/data.txt',
        mimetype = 'text/csv',
        charset = 'ascii',
        linesep = parts.LineSeparators.CRLF,
        content = 'header,value\n1,2\n'
    )

    assert part_2.location == 'https://example.com/data.txt'
    assert part_2.mimetype == 'text/csv'
    assert part_2.charset == 'ascii'
    assert part_2.linesep == parts.LineSeparators.CRLF
