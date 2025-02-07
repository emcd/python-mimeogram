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


''' Test fixtures and utilities. '''


from __future__ import annotations

import contextlib
import os
import pathlib
import tempfile
from typing import Iterator

import pytest


@pytest.fixture
def provide_tempdir( ) -> Iterator[ pathlib.Path ]:
    ''' Provides temporary directory for test isolation. '''
    with tempfile.TemporaryDirectory( ) as tmpdir:
        yield pathlib.Path( tmpdir )


@pytest.fixture
def provide_tempenv( ) -> Iterator[ dict[ str, str ] ]:
    ''' Provides isolated environment variables. '''
    original = os.environ.copy( )
    os.environ.clear( )
    yield os.environ # pyright: ignore
    os.environ.clear( )
    os.environ.update( original )


@contextlib.contextmanager
def create_test_files(
    base_dir: pathlib.Path, files: dict[ str, str ]
) -> Iterator[ None ]:
    ''' Creates test files in specified directory. '''
    created: list[ pathlib.Path ] = [ ]
    try: # pylint: disable=too-many-try-statements
        for relpath, content in files.items( ):
            filepath = base_dir / relpath
            filepath.parent.mkdir( parents = True, exist_ok = True )
            filepath.write_text( content )
            created.append( filepath )
        yield
    finally:
        for filepath in reversed( created ):
            if filepath.exists( ): filepath.unlink( )


def acquire_test_mimeogram( name: str ) -> str:
    ''' Acquires test mimeogram from data directory. '''
    from importlib.resources import files
    location = files( 'mimeogram.data.tests.mimeograms' ).joinpath(
        f"{name}.mg" )
    return location.read_text( )


def produce_test_environment( ) -> dict[ str, str ]:
    ''' Produces test environment variables. '''
    return {
        'MIMEOGRAM_LOG_LEVEL': 'DEBUG',
        'MIMEOGRAM_CONFIG_PATH': '/test/config',
        'MIMEOGRAM_DATA_PATH': '/test/data',
    }
