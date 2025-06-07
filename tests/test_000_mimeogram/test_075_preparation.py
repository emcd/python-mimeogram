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


''' Tests for preparation module. '''


import builtins
import logging

from pathlib import Path

import pytest
import pytest_asyncio
from platformdirs import PlatformDirs

from . import PACKAGE_NAME, cache_import_module


BASIC_CONFIG = '''
[example]
key = "value"
number = 42
'''

ENV_CONFIG = '''
[locations]
environment = "{user_configuration}/.env"
'''

CUSTOM_ENV = '''
TEST_KEY=test_value
TEST_PATH=/test/path
'''


@pytest.fixture( autouse = True )
def reset_icecream( ):
    ''' Reset Icecream state before each test. '''
    import icecream
    icecream.install( )  # Reset to defaults
    icecream.ic.enable( )  # Ensure enabled initially
    yield
    # Cleanup by removing ic from builtins if it exists
    if hasattr( builtins, 'ic' ):
        delattr( builtins, 'ic' )


@pytest.fixture( autouse = True )
def reset_logging( ):
    ''' Reset logging state before each test. '''
    scribe = logging.getLogger( PACKAGE_NAME )
    scribe.handlers.clear( )
    scribe.propagate = False
    scribe.setLevel( logging.NOTSET )
    yield


@pytest.fixture
def provide_test_platform_dirs( provide_tempdir ):
    ''' Provides PlatformDirs with user_config_path in test directory. '''
    class PatchedPlatformDirs( PlatformDirs ):
        __slots__ = ( '_test_config_path', )

        def __init__( self, appname: str, ensure_exists: bool = False ):
            super( ).__init__(
                appname = appname, ensure_exists = ensure_exists )
            test_config = Path( provide_tempdir, appname )
            test_config.mkdir( parents = True, exist_ok = True )
            self._test_config_path = test_config

        @property
        def user_config_path( self ) -> Path:
            return self._test_config_path

    return PatchedPlatformDirs( appname = 'test-app', ensure_exists = True )


@pytest_asyncio.fixture
async def provide_exits( ):
    ''' Provides AsyncExitStack for test resources. '''
    imports = cache_import_module( f"{PACKAGE_NAME}.__.imports" )
    async with imports.ExitsAsync( ) as exits:
        yield exits


@pytest.mark.asyncio
async def test_010_basic_preparation( provide_tempdir, provide_exits ):
    ''' Basic preparation creates valid global state. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    app_info = application.Information( name = 'test-app' )
    state = await preparation.prepare(
        exits = provide_exits,
        application = app_info,
        configfile = config_path )
    assert 'test-app' == state.application.name
    assert 'value' == state.configuration[ 'example' ][ 'key' ]
    assert 42 == state.configuration[ 'example' ][ 'number' ]
    assert state.distribution is not None
    assert provide_exits == state.exits


@pytest.mark.asyncio
async def test_020_environment_loading(
    provide_tempdir, provide_tempenv, provide_exits
):
    ''' Preparation loads environment variables when requested. '''
    import os
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_dir = Path( provide_tempdir ) / 'config'
    config_dir.mkdir( parents = True, exist_ok = True )
    config_path = config_dir / 'config.toml'
    config_path.write_text( ENV_CONFIG )
    work_dir = Path( provide_tempdir ) / 'work'
    work_dir.mkdir( parents = True, exist_ok = True )
    env_path = work_dir / '.env'
    env_path.write_text( CUSTOM_ENV )
    original_path = os.getcwd()
    try:
        os.chdir( work_dir )
        app_info = application.Information( name = 'test-app' )
        await preparation.prepare(
            exits = provide_exits,
            application = app_info,
            configfile = config_path,
            environment = True )

        assert 'test_value' == provide_tempenv[ 'TEST_KEY' ]
        assert '/test/path' == provide_tempenv[ 'TEST_PATH' ]
    finally:
        os.chdir( original_path )


@pytest.mark.asyncio
async def test_030_configuration_edits( provide_tempdir, provide_exits ):
    ''' Preparation applies configuration edits correctly. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    dictedits = cache_import_module( f"{PACKAGE_NAME}.__.dictedits" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    edits = (
        dictedits.SimpleEdit(
            address = ( 'example', 'key' ),
            value = 'edited' ),
    )
    app_info = application.Information( name = 'test-app' )
    state = await preparation.prepare(
        exits = provide_exits,
        application = app_info,
        configfile = config_path,
        configedits = edits )
    assert 'edited' == state.configuration[ 'example' ][ 'key' ]
    assert 42 == state.configuration[ 'example' ][ 'number' ]


@pytest.mark.asyncio
async def test_040_inscription_control( provide_tempdir, provide_exits ):
    ''' Preparation configures logging with inscription control. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    inscription = cache_import_module( f"{PACKAGE_NAME}.__.inscription" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    inscription_control = inscription.Control(
        mode = inscription.Modes.Null,
        level = 'error' )
    app_info = application.Information( name = 'test-app' )
    await preparation.prepare(
        exits = provide_exits,
        application = app_info,
        configfile = config_path,
        inscription = inscription_control )
    import logging
    logger = logging.getLogger( PACKAGE_NAME )
    assert logging.ERROR == logger.level
    assert not logger.propagate
    assert any(
        isinstance( handler, logging.NullHandler )
        for handler in logger.handlers )


@pytest.mark.asyncio
async def test_050_default_inscription( provide_tempdir, provide_exits ):
    ''' Preparation uses default inscription control when not specified. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    inscription = cache_import_module( f"{PACKAGE_NAME}.__.inscription" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    default_control = inscription.Control( )
    assert inscription.Modes.Null == default_control.mode
    assert default_control.level is None
    app_info = application.Information( name = 'test-app' )
    await preparation.prepare(
        exits = provide_exits,
        application = app_info,
        configfile = config_path )
    import logging
    logger = logging.getLogger( PACKAGE_NAME )
    assert not logger.propagate
    assert any(
        isinstance( handler, logging.NullHandler )
        for handler in logger.handlers )


@pytest.mark.asyncio
async def test_060_directory_locations( provide_tempdir, provide_exits ):
    ''' Preparation sets up correct directory locations. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    app_info = application.Information( name = 'test-app' )
    state = await preparation.prepare(
        exits = provide_exits,
        application = app_info,
        configfile = config_path )
    assert state.provide_cache_location( ).exists( )
    assert state.provide_data_location( ).exists( )
    assert state.provide_state_location( ).exists( )
    package_data = state.distribution.provide_data_location( )
    assert isinstance( package_data, Path )


@pytest.mark.asyncio
async def test_070_concurrent_initialization( provide_tempdir, provide_exits ):
    ''' Preparation supports concurrent initialization. '''
    import asyncio
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    preparation = cache_import_module( f"{PACKAGE_NAME}.__.preparation" )
    state = cache_import_module( f"{PACKAGE_NAME}.__.state" )
    config_path = Path( provide_tempdir ) / 'config.toml'
    config_path.write_text( BASIC_CONFIG )
    app_info = application.Information( name = 'test-app' )

    async def concurrent_task( ):
        await asyncio.sleep( 0.1 )
        return 'concurrent task completed'

    results = await asyncio.gather(
        preparation.prepare(
            exits = provide_exits,
            application = app_info,
            configfile = config_path ),
        concurrent_task( ) )
    assert isinstance( results[ 0 ], state.Globals )
    assert 'concurrent task completed' == results[ 1 ]
