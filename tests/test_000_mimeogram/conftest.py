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
