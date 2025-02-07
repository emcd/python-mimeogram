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


''' Tests for processes module. '''


import pytest

from . import cache_import_module


def test_000_subprocess_execute_success( ):
    ''' subprocess_execute successfully runs commands. '''
    processes = cache_import_module( 'mimeogram.__.processes' )
    result = processes.subprocess_execute( 'echo', 'test' )
    assert result.returncode == 0


def test_010_subprocess_execute_failure( ):
    ''' subprocess_execute handles command failures. '''
    processes = cache_import_module( 'mimeogram.__.processes' )
    with pytest.raises( FileNotFoundError ):
        processes.subprocess_execute( 'nonexistent_command' )


def test_020_subprocess_execute_empty( ):
    ''' subprocess_execute handles empty arguments appropriately. '''
    processes = cache_import_module( 'mimeogram.__.processes' )
    with pytest.raises( IndexError ):
        processes.subprocess_execute( )
