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


''' Test fixtures. '''

# pylint: disable=redefined-outer-name


import os
import pathlib
import platform
import tempfile
from typing import Iterator

import pytest


@pytest.fixture
def provide_tempdir( ) -> Iterator[ pathlib.Path ]:
    ''' Provides temporary directory for test isolation. '''
    with tempfile.TemporaryDirectory( ) as tmpdir:
        yield pathlib.Path( tmpdir )


@pytest.fixture
def provide_tempenv(
    provide_tempdir: pathlib.Path
) -> Iterator[ dict[ str, str ] ]:
    ''' Provides isolated environment variables with test home directory. '''
    test_home = pathlib.Path( provide_tempdir ) / 'home'
    test_home.mkdir( parents = True, exist_ok = True )
    ( test_home / '.config' ).mkdir( exist_ok = True )
    ( test_home / 'Documents' ).mkdir( exist_ok = True )

    # Back up original environment
    original = os.environ.copy( )

    # Start with clean environment
    os.environ.clear( )

    # Set up minimal test environment
    test_home_str = str( test_home.resolve( ) )  # Get absolute path

    if platform.system( ) == 'Windows':
        # Windows prioritizes USERPROFILE
        os.environ[ 'USERPROFILE' ] = test_home_str
        # Split into drive and path for HOMEDRIVE/HOMEPATH
        drive, path = os.path.splitdrive( test_home_str )
        os.environ[ 'HOMEDRIVE' ] = drive
        os.environ[ 'HOMEPATH' ] = path
    else:
        # Unix-like systems primarily use HOME
        os.environ[ 'HOME' ] = test_home_str

    yield os.environ # pyright: ignore

    # Restore original environment
    os.environ.clear( )
    os.environ.update( original )
