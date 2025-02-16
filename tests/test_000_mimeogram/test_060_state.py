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


''' Tests for state module. '''

# pylint: disable=redefined-outer-name


from contextlib import AsyncExitStack
from pathlib import Path

import pytest
from platformdirs import PlatformDirs

from . import cache_import_module


@pytest.fixture
def provide_globals( ):
    ''' Provides test globals instance. '''
    state = cache_import_module( 'mimeogram.__.state' )
    application = cache_import_module( 'mimeogram.__.application' )
    distribution = cache_import_module( 'mimeogram.__.distribution' )

    app_info = application.Information( name = 'test-app' )
    platform_dirs = app_info.produce_platform_directories( )
    dist_info = distribution.Information(
        name = 'test-dist',
        location = Path( '/test/path' ),
        editable = True )
    config = { 'locations': { } }
    exits = AsyncExitStack( )

    return state.Globals(
        application = app_info,
        configuration = config,
        directories = platform_dirs,
        distribution = dist_info,
        exits = exits )


def test_010_directory_species_values( ):
    ''' DirectorySpecies enum has expected values. '''
    state = cache_import_module( 'mimeogram.__.state' )
    assert 'cache' == state.DirectorySpecies.Cache.value
    assert 'data' == state.DirectorySpecies.Data.value
    assert 'state' == state.DirectorySpecies.State.value


def test_020_directory_species_members( ):
    ''' DirectorySpecies enum has expected members. '''
    state = cache_import_module( 'mimeogram.__.state' )
    assert set( ( 'Cache', 'Data', 'State' ) ) == {
        member.name for member in state.DirectorySpecies }


def test_110_globals_attributes( provide_globals ):
    ''' Globals class has expected attributes. '''
    globals_obj = provide_globals

    assert 'test-app' == globals_obj.application.name
    assert isinstance( globals_obj.configuration, dict )
    assert isinstance( globals_obj.directories, PlatformDirs )
    assert 'test-dist' == globals_obj.distribution.name
    assert isinstance( globals_obj.exits, AsyncExitStack )


def test_120_globals_immutability( provide_globals ):
    ''' Globals class is immutable. '''
    globals_obj = provide_globals

    with pytest.raises( AttributeError ):
        globals_obj.application = None

    with pytest.raises( AttributeError ):
        globals_obj.configuration = { }

    with pytest.raises( AttributeError ):
        globals_obj.directories = None


def test_130_globals_as_dictionary( provide_globals ):
    ''' Globals.as_dictionary provides shallow copy of state. '''
    globals_obj = provide_globals
    state_dict = globals_obj.as_dictionary( )

    assert isinstance( state_dict, dict )
    assert globals_obj.application == state_dict[ 'application' ]
    assert globals_obj.configuration == state_dict[ 'configuration' ]
    assert globals_obj.directories == state_dict[ 'directories' ]
    assert globals_obj.distribution == state_dict[ 'distribution' ]
    assert globals_obj.exits == state_dict[ 'exits' ]


def test_140_provide_cache_location( provide_globals ):
    ''' Globals.provide_cache_location resolves cache paths. '''
    import sys
    globals_obj = provide_globals
    base_path = globals_obj.provide_cache_location( )
    assert isinstance( base_path, Path )

    if sys.platform == 'win32':
        assert 'Cache' in base_path.parts
        assert 'test-app' in base_path.parent.parts
    else: assert base_path.name == 'test-app'

    subdir_path = globals_obj.provide_cache_location( 'subdir', 'file.txt' )
    assert subdir_path.parts[ -2: ] == ( 'subdir', 'file.txt' )


def test_150_provide_data_location( provide_globals ):
    ''' Globals.provide_data_location resolves data paths. '''
    import sys
    globals_obj = provide_globals
    base_path = globals_obj.provide_data_location( )
    assert isinstance( base_path, Path )

    if sys.platform == 'win32':
        assert 'test-app' in base_path.parts
    else: assert base_path.name == 'test-app'

    subdir_path = globals_obj.provide_data_location( 'subdir', 'file.txt' )
    assert subdir_path.parts[ -2: ] == ( 'subdir', 'file.txt' )


def test_160_provide_state_location( provide_globals ):
    ''' Globals.provide_state_location resolves state paths. '''
    import sys
    globals_obj = provide_globals
    base_path = globals_obj.provide_state_location( )
    assert isinstance( base_path, Path )

    if sys.platform == 'win32':
        assert 'test-app' in base_path.parts
    else: assert base_path.name == 'test-app'

    subdir_path = globals_obj.provide_state_location( 'subdir', 'file.txt' )
    assert subdir_path.parts[ -2: ] == ( 'subdir', 'file.txt' )


def test_170_provide_location_default( provide_globals ):
    ''' Globals.provide_location uses platform defaults without config. '''
    globals_obj = provide_globals
    state = cache_import_module( 'mimeogram.__.state' )

    # Test each species with default behavior (no custom config)
    for species in state.DirectorySpecies:
        base_dir = getattr(
            globals_obj.directories, f'user_{species.value}_path' )
        path = globals_obj.provide_location( species )
        assert path == base_dir

        # Test with appendages
        path_with_appendages = globals_obj.provide_location(
            species, 'subdir', 'file.txt' )
        assert path_with_appendages == base_dir / 'subdir' / 'file.txt'


def test_180_provide_location_with_custom_paths( provide_globals ):
    ''' Globals.provide_location uses custom paths from config. '''
    globals_obj = provide_globals
    state = cache_import_module( 'mimeogram.__.state' )

    # Update configuration with absolute custom paths
    globals_obj.configuration[ 'locations' ] = { }
    paths_by_species = {
        'cache': '/var/cache',
        'data': '/var/lib',
        'state': '/var/run'
    }
    for species in state.DirectorySpecies:
        globals_obj.configuration[ 'locations' ][ species.value ] = (
            f"{paths_by_species[ species.value ]}/{{application_name}}" )

    # Test each species
    for species in state.DirectorySpecies:
        path = globals_obj.provide_location( species )
        assert path == Path( paths_by_species[ species.value ] ) / 'test-app'

        # Test with appendages
        path_with_appendages = globals_obj.provide_location(
            species, 'subdir', 'file.txt' )
        assert path_with_appendages == (
            Path( paths_by_species[ species.value ] )
            / 'test-app' / 'subdir' / 'file.txt' )


def test_190_provide_location_with_variables( provide_globals ):
    ''' Globals.provide_location handles variable substitution. '''
    import sys
    globals_obj = provide_globals
    state = cache_import_module( 'mimeogram.__.state' )

    # Test home variable substitution with platform-aware paths
    if sys.platform == 'win32':
        path_template = '{user_home}\\AppData\\Local\\{application_name}'
    else: path_template = '{user_home}/.local/share/{application_name}'

    globals_obj.configuration[ 'locations' ] = {
        'data': path_template
    }

    path = globals_obj.provide_location( state.DirectorySpecies.Data )
    if sys.platform == 'win32':
        assert 'AppData' in path.parts
        assert 'Local' in path.parts
        assert 'test-app' in path.parts
    else: assert path == Path.home( ) / '.local' / 'share' / 'test-app'

    # Test platform directory variable substitution
    globals_obj.configuration[ 'locations' ] = { }
    for species in state.DirectorySpecies:
        globals_obj.configuration[ 'locations' ][ species.value ] = (
            f"{{user_{species.value}}}/custom" )

    for species in state.DirectorySpecies:
        base_dir = getattr(
            globals_obj.directories, f'user_{species.value}_path' )
        path = globals_obj.provide_location( species )
        assert path == base_dir / 'custom'
