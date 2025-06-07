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


''' Tests for environment module. '''


import os
from pathlib import Path

import pytest
from platformdirs import PlatformDirs

from . import PACKAGE_NAME, cache_import_module, create_test_files


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


@pytest.fixture
def provide_test_state(
    provide_tempdir, provide_tempenv, provide_test_platform_dirs
):
    ''' Provides test state with environment configuration. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    distribution = cache_import_module( f"{PACKAGE_NAME}.__.distribution" )
    state = cache_import_module( f"{PACKAGE_NAME}.__.state" )

    # Create separate project directory
    project_dir = Path( provide_tempdir ) / 'project'
    project_dir.mkdir( parents = True, exist_ok = True )

    app_info = application.Information( name = 'test-app' )
    dist_info = distribution.Information(
        name = 'test-dist',
        location = project_dir,
        editable = True )
    config = {
        'locations': {
            'environment': '{user_configuration}/.env'
        }
    }

    return state.Globals(
        application = app_info,
        configuration = config,
        directories = provide_test_platform_dirs,
        distribution = dist_info,
        exits = provide_tempenv )


@pytest.fixture
def provide_noneditable_state(
    provide_tempdir, provide_tempenv, provide_test_platform_dirs
):
    ''' Provides test state for non-editable installation. '''
    application = cache_import_module( f"{PACKAGE_NAME}.__.application" )
    distribution = cache_import_module( f"{PACKAGE_NAME}.__.distribution" )
    state = cache_import_module( f"{PACKAGE_NAME}.__.state" )

    app_info = application.Information( name = 'test-app' )
    dist_info = distribution.Information(
        name = 'test-dist',
        location = provide_tempdir,
        editable = False )
    config = {
        'locations': {
            'environment': '{user_configuration}/.env'
        }
    }

    return state.Globals(
        application = app_info,
        configuration = config,
        directories = provide_test_platform_dirs,
        distribution = dist_info,
        exits = provide_tempenv )


# Test Files - Development Mode
PROJECT_ENV = '''
TEST_KEY=project_value
TEST_PATH=/project/path
OTHER_KEY=other_value
'''

# Test Files - Normal Installation
LOCAL_ENV = '''
TEST_KEY=local_value
TEST_PATH=/local/path
'''

CONFIGURED_ENV = '''
TEST_KEY=configured_value
TEST_PATH=/configured/path
OTHER_KEY=other_value
'''

MULTIPLE_ENV = '''
TEST_KEY1=value1
TEST_KEY2=value2
'''

BAD_ENV = '''
BAD_KEY=missing_quote'
GOOD_KEY=value
'''


# Development Mode Tests

@pytest.mark.asyncio
async def test_010_development_project_env(
    provide_test_state, provide_tempdir
):
    ''' Project .env is used exclusively in editable install. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )

    # Create project .env and local/configured files that should be ignored
    project_env = Path( provide_test_state.distribution.location ) / '.env'
    project_env.write_text( PROJECT_ENV )

    test_files = { '.env': LOCAL_ENV }
    with create_test_files( provide_tempdir, test_files ):
        user_config = Path( provide_test_state.directories.user_config_path )
        user_config.mkdir( parents = True, exist_ok = True )
        ( user_config / '.env' ).write_text( CONFIGURED_ENV )

        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_test_state )
            assert 'project_value' == provide_test_state.exits[ 'TEST_KEY' ]
            assert '/project/path' == provide_test_state.exits[ 'TEST_PATH' ]
            assert 'other_value' == provide_test_state.exits[ 'OTHER_KEY' ]
        finally:
            os.chdir( initial_path )


@pytest.mark.asyncio
async def test_020_development_directory_env( provide_test_state ):
    ''' Project directory .env files are all loaded in editable install. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )

    # Create project .env directory with multiple files
    project_env = Path( provide_test_state.distribution.location ) / '.env'
    project_env.mkdir( parents = True, exist_ok = True )
    ( project_env / 'first.env' ).write_text( '''
TEST_KEY1=first_value
TEST_PATH1=/first/path
''' )
    ( project_env / 'second.env' ).write_text( '''
TEST_KEY2=second_value
TEST_PATH2=/second/path
''' )

    await environment.update( provide_test_state )
    assert 'first_value' == provide_test_state.exits[ 'TEST_KEY1' ]
    assert '/first/path' == provide_test_state.exits[ 'TEST_PATH1' ]
    assert 'second_value' == provide_test_state.exits[ 'TEST_KEY2' ]
    assert '/second/path' == provide_test_state.exits[ 'TEST_PATH2' ]


@pytest.mark.asyncio
async def test_030_development_fallback( provide_test_state, provide_tempdir ):
    ''' Without project .env, editable falls back to normal behavior. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )

    # Create local and configured .env files
    test_files = { '.env': LOCAL_ENV }
    with create_test_files( provide_tempdir, test_files ):
        user_config = Path( provide_test_state.directories.user_config_path )
        user_config.mkdir( parents = True, exist_ok = True )
        ( user_config / '.env' ).write_text( CONFIGURED_ENV )

        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_test_state )
            assert 'local_value' == provide_test_state.exits[ 'TEST_KEY' ]
            assert '/local/path' == provide_test_state.exits[ 'TEST_PATH' ]
            assert 'other_value' == provide_test_state.exits[ 'OTHER_KEY' ]
        finally:
            os.chdir( initial_path )


# Normal Installation Tests

@pytest.mark.asyncio
async def test_110_normal_local_only(
    provide_noneditable_state, provide_tempdir
):
    ''' Local .env is loaded in non-editable install. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )
    test_files = { '.env': LOCAL_ENV }

    with create_test_files( provide_tempdir, test_files ):
        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_noneditable_state )
            assert (
                'local_value'
                == provide_noneditable_state.exits[ 'TEST_KEY' ] )
            assert (
                '/local/path'
                == provide_noneditable_state.exits[ 'TEST_PATH' ] )
        finally:
            os.chdir( initial_path )


@pytest.mark.asyncio
async def test_120_normal_configured_only( provide_noneditable_state ):
    ''' Configured .env is loaded in non-editable install. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )

    user_config = Path(
        provide_noneditable_state.directories.user_config_path )
    user_config.mkdir( parents = True, exist_ok = True )
    ( user_config / '.env' ).write_text( CONFIGURED_ENV )

    await environment.update( provide_noneditable_state )
    assert 'configured_value' == provide_noneditable_state.exits[ 'TEST_KEY' ]
    assert '/configured/path' == provide_noneditable_state.exits[ 'TEST_PATH' ]


@pytest.mark.asyncio
async def test_130_normal_merged( provide_noneditable_state, provide_tempdir ):
    ''' Local and configured .env files are merged in non-editable install. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )
    test_files = { '.env': LOCAL_ENV }

    with create_test_files( provide_tempdir, test_files ):
        user_config = Path(
            provide_noneditable_state.directories.user_config_path )
        user_config.mkdir( parents = True, exist_ok = True )
        ( user_config / '.env' ).write_text( CONFIGURED_ENV )

        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_noneditable_state )
            # Local values should override configured values
            assert (
                'local_value'
                == provide_noneditable_state.exits[ 'TEST_KEY' ] )
            assert (
                '/local/path'
                == provide_noneditable_state.exits[ 'TEST_PATH' ] )
            # Non-overridden configured values should persist
            assert (
                'other_value'
                == provide_noneditable_state.exits[ 'OTHER_KEY' ] )
        finally:
            os.chdir( initial_path )


@pytest.mark.asyncio
async def test_140_normal_no_template(
    provide_noneditable_state, provide_tempdir
):
    ''' Local .env still works when no configuration template exists. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )

    # Remove environment template from configuration
    provide_noneditable_state.configuration.clear( )

    test_files = { '.env': LOCAL_ENV }
    with create_test_files( provide_tempdir, test_files ):
        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_noneditable_state )
            assert (
                'local_value'
                == provide_noneditable_state.exits[ 'TEST_KEY' ] )
            assert (
                '/local/path'
                == provide_noneditable_state.exits[ 'TEST_PATH' ] )
        finally:
            os.chdir( initial_path )


# Error Cases

@pytest.mark.asyncio
async def test_210_no_env_files( provide_noneditable_state ):
    ''' Update handles missing .env files gracefully. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )
    initial_env = provide_noneditable_state.exits.copy( )
    await environment.update( provide_noneditable_state )
    assert initial_env == provide_noneditable_state.exits


@pytest.mark.asyncio
async def test_220_invalid_env_file(
    provide_noneditable_state, provide_tempdir
):
    ''' Update handles invalid .env files appropriately. '''
    environment = cache_import_module( f"{PACKAGE_NAME}.__.environment" )
    test_files = { '.env': BAD_ENV }

    with create_test_files( provide_tempdir, test_files ):
        initial_path = os.getcwd( )
        try:
            os.chdir( provide_tempdir )
            await environment.update( provide_noneditable_state )
            # Good entries should still be loaded even if some are malformed
            assert 'value' == provide_noneditable_state.exits[ 'GOOD_KEY' ]
        finally:
            os.chdir( initial_path )
