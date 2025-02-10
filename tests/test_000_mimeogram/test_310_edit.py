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


''' Tests for edit module. '''


import os
import subprocess

import pytest

from . import PACKAGE_NAME, cache_import_module


def test_000_content_edit_with_mocked_editor( ):
    ''' Verifies content editing functionality using a mocked editor. '''
    edit = cache_import_module( f"{PACKAGE_NAME}.edit" )
    call_tracker = { 'editor_called': False }
    initial_content = 'Initial content'
    new_content = 'Edited content'

    def mock_editor_executor( filename: str ) -> str:
        call_tracker[ 'editor_called' ] = True
        assert os.path.exists( filename )
        with open( filename, 'r', encoding = 'utf-8' ) as f:
            assert initial_content == f.read( )
        return new_content

    def mock_editor_discoverer():
        return mock_editor_executor

    edited_content = edit.edit_content(
        initial_content,
        suffix = '.txt',
        editor_discoverer = mock_editor_discoverer )
    assert call_tracker[ 'editor_called' ]
    assert edited_content == new_content


def test_010_content_edit_without_editor( ):
    ''' Validates behavior when no editor is available. '''
    edit = cache_import_module( f"{PACKAGE_NAME}.edit" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    def mock_editor_discoverer():
        raise exceptions.ProgramAbsenceError( 'editor' )

    initial_content = 'Original content'
    edited_content = edit.edit_content(
        initial_content, editor_discoverer = mock_editor_discoverer )
    assert edited_content == initial_content


def test_020_content_edit_with_editor_error( ):
    ''' Confirms proper error handling when editor execution fails. '''
    edit = cache_import_module( f"{PACKAGE_NAME}.edit" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    def mock_editor_executor( filename: str ) -> str:
        raise subprocess.SubprocessError( "Simulated editor failure" )

    with pytest.raises( exceptions.EditorFailure ):
        edit.edit_content(
            'Test edit content with editor error',
            editor_discoverer = lambda: mock_editor_executor )
