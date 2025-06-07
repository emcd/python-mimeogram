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


''' Tests for configuration module. '''


from pathlib import Path

import pytest
from platformdirs import PlatformDirs

from . import cache_import_module, create_test_files


# Test TOML configurations
BASIC_CONFIG = '''
[example]
key = "value"
number = 42
'''

MAIN_CONFIG = '''
includes = [ "{user_configuration}/include.toml" ]
[main]
key = "main value"
'''

INCLUDE_CONFIG = '''
[include]
key = "included value"
'''

SECTION_CONFIG = '''
[section]
key = "original"
[[section.nested]]
value = "unchanged"
'''

TEMPLATE_CONFIG = '''
[template]
key = "template value"
'''

USER_CONFIG = '''
[existing]
key = "user value"
'''

INVALID_CONFIG = '''
[invalid
key = unclosed string'
'''


@pytest.fixture
def provide_test_platform_dirs( provide_tempdir ):
    ''' Provides PlatformDirs with user_config_path in test directory.

        Works consistently across all platforms by forcing the config path
        to a known test location.
    '''
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
def provide_test_distribution( provide_tempdir ):
    ''' Provides test distribution configuration.

        Creates a mock distribution with temporary location for testing.
    '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )
    return distribution.Information(
        name = 'test-dist',
        location = provide_tempdir,
        editable = True )


def test_010_enablement_tristate_values( ):
    ''' EnablementTristate enum has expected values. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    assert 'disable' == configuration.EnablementTristate.Disable.value
    assert 'retain' == configuration.EnablementTristate.Retain.value
    assert 'enable' == configuration.EnablementTristate.Enable.value


def test_020_enablement_tristate_bool_conversion( ):
    ''' EnablementTristate converts to bool as expected. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    exceptions = cache_import_module( 'mimeogram.__.exceptions' )
    assert not bool( configuration.EnablementTristate.Disable )
    assert bool( configuration.EnablementTristate.Enable )
    with pytest.raises( exceptions.OperationInvalidity ):
        bool( configuration.EnablementTristate.Retain )


def test_030_enablement_tristate_is_retain( ):
    ''' EnablementTristate.is_retain works as expected. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    assert not configuration.EnablementTristate.Disable.is_retain( )
    assert configuration.EnablementTristate.Retain.is_retain( )
    assert not configuration.EnablementTristate.Enable.is_retain( )


@pytest.mark.asyncio
async def test_100_acquire_basic_config(
    provide_tempdir, provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition loads basic TOML file. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    imports = cache_import_module( 'mimeogram.__.imports' )
    test_files = { 'general.toml': BASIC_CONFIG }
    with create_test_files( provide_tempdir, test_files ):
        config = await configuration.acquire(
            application_name = 'test-app',
            directories = provide_test_platform_dirs,
            distribution = provide_test_distribution,
            file = provide_tempdir / 'general.toml' )
        assert isinstance( config, imports.AccretiveDictionary )
        assert 'value' == config[ 'example' ][ 'key' ]
        assert 42 == config[ 'example' ][ 'number' ]


@pytest.mark.asyncio
async def test_110_acquire_with_includes(
    provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition processes includes correctly. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    config_dir = Path( provide_test_platform_dirs.user_config_path )
    ( config_dir / 'general.toml' ).write_text( MAIN_CONFIG )
    ( config_dir / 'include.toml' ).write_text( INCLUDE_CONFIG )
    config = await configuration.acquire(
        application_name = 'test-app',
        directories = provide_test_platform_dirs,
        distribution = provide_test_distribution,
        file = config_dir / 'general.toml' )
    assert config[ 'main' ][ 'key' ] == 'main value'
    assert config[ 'include' ][ 'key' ] == 'included value'


@pytest.mark.asyncio
async def test_120_acquire_with_edits(
    provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition applies dictionary edits. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    dictedits = cache_import_module( 'mimeogram.__.dictedits' )
    config_dir = Path( provide_test_platform_dirs.user_config_path )
    ( config_dir / 'general.toml' ).write_text( SECTION_CONFIG )
    edits = (
        dictedits.SimpleEdit(
            address = ( 'section', 'key' ),
            value = 'edited' ),
        dictedits.ElementsEntryEdit(
            address = ( 'section', 'nested' ),
            editee = ( 'value', 'changed' ) )
    )
    config = await configuration.acquire(
        application_name = 'test-app',
        directories = provide_test_platform_dirs,
        distribution = provide_test_distribution,
        edits = edits,
        file = config_dir / 'general.toml' )
    assert config[ 'section' ][ 'key' ] == 'edited'
    assert config[ 'section' ][ 'nested' ][ 0 ][ 'value' ] == 'changed'


@pytest.mark.asyncio
async def test_130_acquire_template_copy(
    provide_tempdir, provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition copies template when no config exists. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    dist_config_dir = Path( provide_tempdir, 'data', 'configuration' )
    dist_config_dir.mkdir( parents = True, exist_ok = True )
    ( dist_config_dir / 'general.toml' ).write_text( TEMPLATE_CONFIG )
    config = await configuration.acquire(
        application_name = 'test-app',
        directories = provide_test_platform_dirs,
        distribution = provide_test_distribution )
    assert config[ 'template' ][ 'key' ] == 'template value'


@pytest.mark.asyncio
async def test_135_acquire_template_already_exists(
    provide_tempdir, provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition preserves existing config file. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    dist_config_dir = Path( provide_tempdir, 'data', 'configuration' )
    dist_config_dir.mkdir( parents = True, exist_ok = True )
    ( dist_config_dir / 'general.toml' ).write_text( TEMPLATE_CONFIG )
    config_dir = Path( provide_test_platform_dirs.user_config_path )
    ( config_dir / 'general.toml' ).write_text( USER_CONFIG )
    config = await configuration.acquire(
        application_name = 'test-app',
        directories = provide_test_platform_dirs,
        distribution = provide_test_distribution )
    assert 'existing' in config
    assert config[ 'existing' ][ 'key' ] == 'user value'
    assert 'template' not in config


@pytest.mark.asyncio
async def test_140_acquire_error_handling(
    provide_test_distribution, provide_test_platform_dirs
):
    ''' Configuration acquisition handles invalid TOML appropriately. '''
    configuration = cache_import_module( 'mimeogram.__.configuration' )
    config_dir = Path( provide_test_platform_dirs.user_config_path )
    ( config_dir / 'general.toml' ).write_text( INVALID_CONFIG )
    with pytest.raises( Exception ):
        await configuration.acquire(
            application_name = 'test-app',
            directories = provide_test_platform_dirs,
            distribution = provide_test_distribution,
            file = config_dir / 'general.toml' )
