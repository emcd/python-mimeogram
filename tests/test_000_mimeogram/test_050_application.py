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


''' Tests for application module. '''


import pytest
from platformdirs import PlatformDirs

from . import PACKAGE_NAME, cache_import_module


def test_000_information_defaults( ):
    ''' Information class provides expected defaults. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    info = application.Information( )
    assert PACKAGE_NAME == info.name
    assert info.publisher is None
    assert info.version is None


def test_010_information_custom_values( ):
    ''' Information class accepts custom values. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    info = application.Information(
        name = 'custom-app',
        publisher = 'Test Publisher',
        version = '1.0.0' )
    assert 'custom-app' == info.name
    assert 'Test Publisher' == info.publisher
    assert '1.0.0' == info.version


def test_020_information_platform_dirs( ):
    ''' Information class produces PlatformDirs instance. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    info = application.Information( name = 'test-app' )
    platform_dirs = info.produce_platform_directories( )
    assert isinstance( platform_dirs, PlatformDirs )
    assert 'test-app' == platform_dirs.appname
    assert platform_dirs.appauthor is None
    assert platform_dirs.version is None


def test_030_information_platform_dirs_full( ):
    ''' Information class forwards all attributes to PlatformDirs. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    info = application.Information(
        name = 'test-app',
        publisher = 'Test Publisher',
        version = '1.0.0' )
    platform_dirs = info.produce_platform_directories( )
    assert isinstance( platform_dirs, PlatformDirs )
    assert 'test-app' == platform_dirs.appname
    assert 'Test Publisher' == platform_dirs.appauthor
    assert '1.0.0' == platform_dirs.version


def test_040_information_immutability( ):
    ''' Information class is immutable. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    info = application.Information(
        name = 'test-app',
        publisher = 'Test Publisher',
        version = '1.0.0' )
    with pytest.raises( AttributeError ):
        info.name = 'new-name'
