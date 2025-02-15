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


''' Tests for content acquisition module. '''
# pylint: disable=redefined-outer-name


import exceptiongroup
import os
import sys

import httpx
import pytest

from . import (
    PACKAGE_NAME,
    cache_import_module,
    create_test_files,
    produce_test_environment,
)


@pytest.fixture
def provide_auxdata( provide_tempdir, provide_tempenv ):
    ''' Provides test auxiliary data. '''
    from accretive.qaliases import AccretiveDictionary
    from platformdirs import PlatformDirs

    __ = cache_import_module( f"{PACKAGE_NAME}.__" )
    _app = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    _dist = cache_import_module( f"{PACKAGE_NAME}.__.distribution" )

    provide_tempenv.update( produce_test_environment( ) )
    return __.Globals(
        application = _app.Information( name = 'test-app' ),
        configuration = AccretiveDictionary( {
            'acquire-parts': {
                'fail-on-invalid': False,
                'recurse-directories': False
            }
        } ),
        directories = PlatformDirs( appname = 'test-app' ),
        distribution = _dist.Information(
            name = 'test-package',
            location = provide_tempdir / 'test-package',
            editable = True ),
        exits = __.ExitsAsync( ) )


# Basic File Acquisition Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_100_acquire_single_file( provide_tempdir, provide_auxdata ):
    ''' Successfully acquires content from single file. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    test_content = "Test content\nwith multiple lines\n"
    test_files = { "test.txt": test_content }

    with create_test_files( provide_tempdir, test_files ):
        result = await acquirers.acquire(
            provide_auxdata, [ provide_tempdir / "test.txt" ] )

        assert len( result ) == 1
        part = result[ 0 ]
        assert part.location == str( provide_tempdir / "test.txt" )
        assert part.mimetype.startswith( "text/" )
        assert part.charset.lower( ) == "utf-8"
        assert part.content == test_content


@pytest.mark.asyncio
async def test_110_acquire_directory( provide_tempdir, provide_auxdata ):
    ''' Successfully acquires content from directory. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    test_files = {
        "file1.txt": "Content 1\n",
        "file2.txt": "Content 2\n",
    }

    with create_test_files( provide_tempdir, test_files ):
        result = await acquirers.acquire(
            provide_auxdata, [ provide_tempdir ] )

        assert len( result ) == 2
        contents = { part.content for part in result }
        assert contents == { "Content 1\n", "Content 2\n" }


@pytest.mark.asyncio
async def test_120_acquire_recursive_directory(
    provide_tempdir, provide_auxdata
):
    ''' Successfully traverses directory recursively. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    test_files = {
        "file1.txt": "Root content\n",
        "subdir/file2.txt": "Nested content\n",
    }
    provide_auxdata.configuration[
        'acquire-parts' ][ 'recurse-directories' ] = True

    with create_test_files( provide_tempdir, test_files ):
        result = await acquirers.acquire(
            provide_auxdata, [ provide_tempdir ] )

        assert len( result ) == 2
        contents = { part.content for part in result }
        assert contents == { "Root content\n", "Nested content\n" }


# Line Ending Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_200_detect_line_endings( provide_tempdir, provide_auxdata ):
    ''' Successfully detects and normalizes different line endings. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    test_files = {
        "unix.txt": "line1\nline2\n",          # LF
        "windows.txt": "line1\r\nline2\r\n",   # CRLF
        "mac.txt": "line1\rline2\r",           # CR
    }

    with create_test_files( provide_tempdir, test_files ):
        results = await acquirers.acquire( provide_auxdata, [
            provide_tempdir / "unix.txt",
            provide_tempdir / "windows.txt",
            provide_tempdir / "mac.txt",
        ] )

        assert len( results ) == 3
        lineseps = { part.linesep for part in results }
        assert lineseps == {
            parts.LineSeparators.LF,
            parts.LineSeparators.CRLF,
            parts.LineSeparators.CR,
        }
        # All content should be normalized to LF
        for part in results:
            assert part.content.count( '\r\n' ) == 0
            assert part.content.count( '\r' ) == 0
            assert part.content.count( '\n' ) == 2


# Character Set Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_300_detect_charset( provide_tempdir, provide_auxdata ):
    ''' Successfully detects different character sets. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    # Create and populate test files
    utf8_path = provide_tempdir / "utf8bom.txt"
    ascii_path = provide_tempdir / "ascii.txt"
    utf16_path = provide_tempdir / "utf16.txt"
    latin1_path = provide_tempdir / "latin1.txt"

    # Write binary content
    utf8_path.write_bytes(b'\xef\xbb\xbfHello, World!\n')  # UTF-8 with BOM
    ascii_path.write_bytes(b'Hello, World!\n')  # ASCII content
    utf16_path.write_bytes(
        b'\xff\xfeH\x00e\x00l\x00l\x00o\x00!\x00\n\x00')  # UTF-16 LE
    latin1_path.write_bytes(b'Caf\xe9\n')  # ISO-8859-1 / invalid UTF-8

    try:
        results = await acquirers.acquire(
            provide_auxdata, [utf8_path, ascii_path, utf16_path, latin1_path] )

        charsets = { part.charset.lower() for part in results }
        assert 'utf-8' in charsets
        assert 'utf-16' in charsets
        assert 'iso-8859-9' in charsets or 'latin1' in charsets
    finally:
        for path in (utf8_path, ascii_path, utf16_path, latin1_path):
            if path.exists():
                path.unlink()


# MIME Type Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_400_detect_mime_types( provide_tempdir, provide_auxdata ):
    ''' Successfully detects MIME types for different file types. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    test_files = {
        "plain.txt": "Plain text\n",
        "script.py": (
            "#!/usr/bin/env python3\n"
            "from __future__ import annotations\n\n"
            "def hello() -> str:\n    return 'Python'\n" ),
    }

    with create_test_files( provide_tempdir, test_files ):
        results = await acquirers.acquire( provide_auxdata, [
            provide_tempdir / "plain.txt",
            provide_tempdir / "script.py",
        ] )

        mimetypes = { part.mimetype for part in results }
        assert "text/plain" in mimetypes
        assert any( "python" in mt for mt in mimetypes )


# Error Handling Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_500_invalid_file( provide_tempdir, provide_auxdata ):
    ''' Properly handles missing files. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    nonexistent = provide_tempdir / "nonexistent.txt"
    with pytest.raises( exceptions.ContentAcquireFailure ) as excinfo:
        await acquirers.acquire( provide_auxdata, [ nonexistent ] )

    assert str( nonexistent ) in str( excinfo.value )


@pytest.mark.asyncio
async def test_510_unsupported_scheme( provide_auxdata ):
    ''' Properly handles unsupported URL schemes. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    with pytest.raises( exceptions.UrlSchemeNoSupport ) as excinfo:
        await acquirers.acquire(
            provide_auxdata, [ "ftp://example.com/file.txt" ] )

    assert "ftp://example.com/file.txt" in str( excinfo.value )


@pytest.mark.asyncio
async def test_520_nontextual_mime( provide_tempdir, provide_auxdata ):
    ''' Properly handles non-textual MIME types. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    binary_path = provide_tempdir / "binary.bin"
    # Create a binary file with random-looking but consistent content
    binary_path.write_bytes( bytes( [ 0xFF, 0x00 ] * 128 ) )

    try:
        with pytest.raises( exceptiongroup.ExceptionGroup ) as excinfo:
            await acquirers.acquire( provide_auxdata, [ binary_path ] )

        # Check that we have exactly one exception in the group
        assert len( excinfo.value.exceptions ) == 1
        # Check that it's the right type of exception
        assert isinstance(
            excinfo.value.exceptions[ 0 ],
            exceptions.TextualMimetypeInvalidity )
        # Verify the error message includes path and mimetype
        err_msg = str( excinfo.value.exceptions[ 0 ] )
        assert str( binary_path ) in err_msg
        assert 'application/octet-stream' in err_msg
    finally:
        if binary_path.exists( ):
            binary_path.unlink( )


# HTTP Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_600_http_acquisition( provide_auxdata, httpx_mock ):
    ''' Successfully acquires content via HTTP. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    test_content = "Remote content\n"
    httpx_mock.add_response(
        url = "https://example.com/test.txt",
        status_code = 200,
        content = test_content.encode( 'utf-8' ),
        headers = { 'content-type': 'text/plain; charset=utf-8' } )

    result = await acquirers.acquire(
        provide_auxdata, [ "https://example.com/test.txt" ] )

    assert len( result ) == 1
    part = result[ 0 ]
    assert part.location == "https://example.com/test.txt"
    assert part.mimetype == "text/plain"
    assert part.charset == "utf-8"
    assert part.content == test_content


@pytest.mark.asyncio
async def test_610_http_error( provide_auxdata, httpx_mock ):
    ''' Properly handles HTTP errors. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    httpx_mock.add_exception( httpx.HTTPError( "HTTP Error" ) )

    with pytest.raises( exceptiongroup.ExceptionGroup ) as excinfo:
        await acquirers.acquire(
            provide_auxdata, [ "https://example.com/test.txt" ] )

    assert len( excinfo.value.exceptions ) == 1
    assert isinstance(
        excinfo.value.exceptions[0],
        exceptions.ContentAcquireFailure )
    assert "https://example.com/test.txt" in str( excinfo.value.exceptions[0] )


@pytest.mark.asyncio
async def test_620_http_nontextual_mimetype( provide_auxdata, httpx_mock ):
    ''' Properly handles non-textual MIME types in HTTP response. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    httpx_mock.add_response(
        url = "https://example.com/test.bin",
        status_code = 200,
        content = bytes(range(256)),  # Binary content that can't be UTF-8 decoded
        headers = { 'content-type': 'application/octet-stream' } )

    with pytest.raises( exceptiongroup.ExceptionGroup ) as excinfo:
        await acquirers.acquire(
            provide_auxdata, [ "https://example.com/test.bin" ] )

    assert len( excinfo.value.exceptions ) == 1
    assert isinstance(
        excinfo.value.exceptions[0],
        exceptions.TextualMimetypeInvalidity )
    assert "https://example.com/test.bin" in str( excinfo.value.exceptions[0] )


# VCS Directory Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_700_vcs_directory_exclusion( provide_tempdir, provide_auxdata ):
    ''' Successfully excludes VCS directories. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    test_files = {
        "regular.txt": "Regular content\n",
        ".git/config": "Git config\n",
        ".svn/entries": "SVN entries\n",
    }
    provide_auxdata.configuration[
        'acquire-parts' ][ 'recurse-directories' ] = True

    with create_test_files( provide_tempdir, test_files ):
        result = await acquirers.acquire(
            provide_auxdata, [ provide_tempdir ] )

        assert len( result ) == 1
        assert result[ 0 ].content == "Regular content\n"


# Gitignore Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_800_gitignore_patterns( provide_tempdir, provide_auxdata ):
    ''' Successfully applies gitignore patterns. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    test_files = {
        ".gitignore": "*.log\nbuild/\n",
        "app.py": "print('Hello')\n",
        "test.log": "Log content\n",
        "build/output.txt": "Build output\n",
    }
    provide_auxdata.configuration[
        'acquire-parts' ][ 'recurse-directories' ] = True

    with create_test_files( provide_tempdir, test_files ):
        result = await acquirers.acquire(
            provide_auxdata, [ provide_tempdir ] )

        assert len( result ) == 2  # .gitignore and app.py
        contents = { part.content for part in result }
        assert "Log content\n" not in contents
        assert "Build output\n" not in contents


# Edge Case Tests
# ===============================================================================

@pytest.mark.asyncio
async def test_900_nonexistent_file( provide_tempdir, provide_auxdata ):
    ''' Properly handles non-existent files. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    nonexistent = provide_tempdir / "does-not-exist.txt"
    with pytest.raises( exceptions.ContentAcquireFailure ) as excinfo:
        await acquirers.acquire( provide_auxdata, [nonexistent] )
    assert str( nonexistent ) in str( excinfo.value )


@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.platform == "win32",
    reason = "Symlink creation may require special privileges on Windows" )
async def test_910_symlink_file( provide_tempdir, provide_auxdata ):
    ''' Successfully handles symlinked files. '''
    acquirers = cache_import_module( f"{PACKAGE_NAME}.acquirers" )

    # Create target file
    target_path = provide_tempdir / "target.txt"
    target_path.write_text( "Target content\n" )

    # Create symlink
    link_path = provide_tempdir / "link.txt"
    try:
        os.symlink( target_path, link_path )

        results = await acquirers.acquire(
            provide_auxdata, [link_path] )

        assert len( results ) == 1
        assert results[0].content == "Target content\n"
    finally:
        if link_path.exists():
            link_path.unlink()
        if target_path.exists():
            target_path.unlink()
