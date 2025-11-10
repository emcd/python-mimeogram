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
    detextive = cache_import_module( 'detextive' )

    # Check enum values
    assert detextive.LineSeparators.CR.value == '\r'
    assert detextive.LineSeparators.CRLF.value == '\r\n'
    assert detextive.LineSeparators.LF.value == '\n'


def test_010_line_separators_detection( ):
    ''' Line separator detection from bytes. '''
    detextive = cache_import_module( 'detextive' )

    # Test detection of different line separators
    cr_bytes = b'line1\rline2\rline3'
    crlf_bytes = b'line1\r\nline2\r\nline3'
    lf_bytes = b'line1\nline2\nline3'
    mixed_bytes = b'line1\rline2\nline3\r\n'
    double_cr_bytes = b'line1\r\rline2\r\rline3'
    empty_bytes = b''
    no_terminator_bytes = b'line1line2line3'

    assert (
        detextive.LineSeparators.detect_bytes( cr_bytes )
        == detextive.LineSeparators.CR )
    assert (
        detextive.LineSeparators.detect_bytes( crlf_bytes )
        == detextive.LineSeparators.CRLF )
    assert (
        detextive.LineSeparators.detect_bytes( lf_bytes )
        == detextive.LineSeparators.LF )

    # With mixed bytes, it detects the first encountered line separator
    assert (
        detextive.LineSeparators.detect_bytes( mixed_bytes )
        == detextive.LineSeparators.CR )

    # Double CR case
    assert (
        detextive.LineSeparators.detect_bytes( double_cr_bytes )
        == detextive.LineSeparators.CR )

    # Empty bytes and bytes without terminators
    assert detextive.LineSeparators.detect_bytes( empty_bytes ) is None
    assert detextive.LineSeparators.detect_bytes( no_terminator_bytes ) is None


def test_020_line_separators_normalization( ):
    ''' Line separator normalization methods. '''
    detextive = cache_import_module( 'detextive' )

    # Test universal normalization
    mixed_content = "line1\rline2\r\nline3\n"
    normalized = detextive.LineSeparators.normalize_universal( mixed_content )
    assert normalized == "line1\nline2\nline3\n"

    # Test specific separator nativization and normalization
    cr_content = "line1\rline2\rline3"
    lf_sep = detextive.LineSeparators.LF
    cr_sep = detextive.LineSeparators.CR
    crlf_sep = detextive.LineSeparators.CRLF

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
    detextive = cache_import_module( 'detextive' )
    import pytest
    from frigid.exceptions import AttributeImmutability

    # Create a Part instance
    part = parts.Part(
        location = 'test.txt',
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = detextive.LineSeparators.LF,
        content = 'test content'
    )

    # Verify immutability through frigid
    with pytest.raises( AttributeImmutability ):
        part.location = 'new.txt'
    with pytest.raises( AttributeImmutability ):
        part.mimetype = 'application/json'
    with pytest.raises( AttributeImmutability ):
        part.charset = 'ascii'
    with pytest.raises( AttributeImmutability ):
        part.linesep = detextive.LineSeparators.CRLF
    with pytest.raises( AttributeImmutability ):
        part.content = 'new content'


def test_110_part_creation( ):
    ''' Creating Part instances with different parameters. '''
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    detextive = cache_import_module( 'detextive' )

    # Test with various valid inputs
    part_1 = parts.Part(
        location = '/path/to/file.txt',
        mimetype = 'text/plain',
        charset = 'utf-8',
        linesep = detextive.LineSeparators.LF,
        content = 'Sample text content'
    )

    # Verify all attributes are set correctly
    assert part_1.location == '/path/to/file.txt'
    assert part_1.mimetype == 'text/plain'
    assert part_1.charset == 'utf-8'
    assert part_1.linesep == detextive.LineSeparators.LF
    assert part_1.content == 'Sample text content'

    # Test with URL location
    part_2 = parts.Part(
        location = 'https://example.com/data.txt',
        mimetype = 'text/csv',
        charset = 'ascii',
        linesep = detextive.LineSeparators.CRLF,
        content = 'header,value\n1,2\n'
    )

    assert part_2.location == 'https://example.com/data.txt'
    assert part_2.mimetype == 'text/csv'
    assert part_2.charset == 'ascii'
    assert part_2.linesep == detextive.LineSeparators.CRLF
