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


''' Tests for platform-specific filesystem protection. '''


import sys

import pytest

from . import PACKAGE_NAME, cache_import_module


@pytest.mark.skipif( 'win32' == sys.platform, reason = 'Unix-only test' )
@pytest.mark.skipif( 'darwin' == sys.platform, reason = 'Unix-only test' )
def test_100_unix_system_paths( ):
    ''' Unix system paths return frozen set. '''
    unix = cache_import_module( f"{PACKAGE_NAME}.fsprotect.unix" )
    paths = unix.discover_system_paths( )
    assert isinstance( paths, frozenset )
    assert all( isinstance( path, unix.__.Path ) for path in paths )


@pytest.mark.skipif( 'darwin' != sys.platform, reason = 'macOS-only test' )
def test_200_macos_system_paths( ):
    ''' macOS system paths return frozen set. '''
    macos = cache_import_module( f"{PACKAGE_NAME}.fsprotect.macos" )
    paths = macos.discover_system_paths( )
    assert isinstance( paths, frozenset )
    assert all( isinstance( path, macos.__.Path ) for path in paths )


@pytest.mark.skipif( 'darwin' != sys.platform, reason = 'macOS-only test' )
def test_210_macos_user_paths( ):
    ''' macOS user paths return frozen set. '''
    macos = cache_import_module( f"{PACKAGE_NAME}.fsprotect.macos" )
    paths = macos.discover_user_paths( )
    assert isinstance( paths, frozenset )
    assert all( isinstance( path, macos.__.Path ) for path in paths )


@pytest.mark.skipif( 'win32' != sys.platform, reason = 'Windows-only test' )
def test_300_windows_system_paths( ):
    ''' Windows system paths return frozen set. '''
    windows = cache_import_module( f"{PACKAGE_NAME}.fsprotect.windows" )
    paths = windows.discover_system_paths( )
    assert isinstance( paths, frozenset )
    assert all( isinstance( path, windows.__.Path ) for path in paths )


@pytest.mark.skipif( 'win32' != sys.platform, reason = 'Windows-only test' )
def test_310_windows_user_paths( ):
    ''' Windows user paths return frozen set. '''
    windows = cache_import_module( f"{PACKAGE_NAME}.fsprotect.windows" )
    paths = windows.discover_user_paths( )
    assert isinstance( paths, frozenset )
    assert all( isinstance( path, windows.__.Path ) for path in paths )
