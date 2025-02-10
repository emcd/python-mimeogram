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


''' Tests for display module. '''


import os
import subprocess

import pytest

from . import PACKAGE_NAME, cache_import_module


def test_000_content_display_with_mocked_pager( ):
    ''' Verifies display content functionality using a mocked pager. '''
    display = cache_import_module( f"{PACKAGE_NAME}.display" )
    call_tracker = { 'pager_called': False }
    content = 'Test display content'

    def mock_pager_executor( filename: str ) -> None:
        call_tracker[ 'pager_called' ] = True
        assert os.path.exists( filename )
        with open( filename, 'r', encoding = 'utf-8' ) as f:
            assert content == f.read( )

    def mock_pager_discoverer( ):
        return mock_pager_executor

    display.display_content(
        content, suffix = '.txt', pager_discoverer = mock_pager_discoverer )
    assert call_tracker[ 'pager_called' ]


def test_010_content_display_with_subprocess_error( ):
    ''' Confirms proper error handling when pager execution fails. '''
    display = cache_import_module( f"{PACKAGE_NAME}.display" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    def mock_pager_executor( filename: str ) -> None:
        raise subprocess.SubprocessError( "Simulated pager failure" )

    with pytest.raises( exceptions.PagerFailure ):
        display.display_content(
            'Test display content with pager error',
            pager_discoverer = lambda: mock_pager_executor )
