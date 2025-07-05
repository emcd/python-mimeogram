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


''' Tests for filesystem protection cache. '''


from pathlib import Path

import pytest

from . import PACKAGE_NAME, cache_import_module


def _nativize_path( path_str: str ) -> str:
    ''' Converts path string to platform-native format. '''
    import sys
    if sys.platform == 'win32' and path_str.startswith( '/' ):
        return f"C:{path_str}"
    return path_str


def test_100_rule_initialization( ):
    ''' Rule initializes with paths and optional patterns. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    # Test with just paths
    paths = frozenset( [ Path( '/test/path' ) ] )
    rule = cache.Rule( paths = paths )
    assert rule.paths == paths
    assert rule.patterns == frozenset( )

    # Test with paths and patterns
    patterns = frozenset( [ '**/*.secret' ] )
    rule = cache.Rule( paths = paths, patterns = patterns )
    assert rule.paths == paths
    assert rule.patterns == patterns


def test_110_rule_immutability( ):
    ''' Rule objects are immutable. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    paths = frozenset( [ Path( '/test/path' ) ] )
    patterns = frozenset( [ '**/*.secret' ] )
    rule = cache.Rule( paths = paths, patterns = patterns )

    with pytest.raises( AttributeError ):
        rule.paths = frozenset( [ Path( '/other/path' ) ] )

    with pytest.raises( AttributeError ):
        rule.patterns = frozenset( [ '**/*.other' ] )


def test_200_cache_initialization( ):
    ''' Cache initializes with basic configuration. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create simple rules dictionary
    test_rule = cache.Rule( paths = frozenset( [ Path( '/test/path' ) ] ) )
    rules = { core.Reasons.CustomAddition: test_rule }

    # Create minimal cache
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = cache.__.immut.Dictionary( ) )

    assert cache_obj.rules == rules
    assert cache_obj.defaults_disablement == frozenset( )
    assert cache_obj.rules_supercession == cache.__.immut.Dictionary( )


def test_210_cache_verify_unprotected( ):
    ''' Cache correctly identifies unprotected paths. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create cache with single protected path
    test_rule = cache.Rule(
        paths = frozenset( [ Path( '/protected/path' ) ] ) )
    rules = { core.Reasons.CustomAddition: test_rule }
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = cache.__.immut.Dictionary( ) )

    # Test unprotected path
    status = cache_obj.verify( Path( '/unprotected/path' ) )
    assert not status.active
    assert status.reason is None
    assert status.description == 'Not protected'


def test_220_cache_verify_protected_path( ):
    ''' Cache correctly identifies protected paths. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create cache with protected path
    protected_path = Path( '/protected/path' )
    test_rule = cache.Rule( paths = frozenset( [ protected_path ] ) )
    rules = { core.Reasons.Credentials: test_rule }
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = cache.__.immut.Dictionary( ) )

    # Test exact path match
    status = cache_obj.verify( protected_path )
    assert status.active
    assert status.reason == core.Reasons.Credentials

    # Test subdirectory
    subpath = protected_path / 'subdir'
    status = cache_obj.verify( subpath )
    assert status.active
    assert status.reason == core.Reasons.Credentials


def test_230_cache_verify_protected_pattern( ):
    ''' Cache correctly identifies paths matching protection patterns. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create cache with pattern protection
    test_rule = cache.Rule(
        paths = frozenset( ),
        patterns = frozenset( [ '**/secrets/**' ] ) )
    rules = { core.Reasons.Credentials: test_rule }
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = cache.__.immut.Dictionary( ) )

    # Test matching path
    status = cache_obj.verify( Path( '/some/path/secrets/file.txt' ) )
    assert status.active
    assert status.reason == core.Reasons.Credentials

    # Test non-matching path
    status = cache_obj.verify( Path( '/some/path/normal/file.txt' ) )
    assert not status.active


def test_240_cache_verify_defaults_disablement( ):
    ''' Cache respects defaults disablement configuration. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create cache with protected path but disabled default
    protected_path = Path( '/protected/path' )
    test_rule = cache.Rule( paths = frozenset( [ protected_path ] ) )
    rules = { core.Reasons.Credentials: test_rule }
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( [ 'protected' ] ),
        rules_supercession = cache.__.immut.Dictionary( ) )

    # Test path that would be protected but is disabled
    status = cache_obj.verify( protected_path )
    assert not status.active


def test_250_cache_verify_rules_supercession( ):
    ''' Cache correctly applies rules supercession. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Create cache with supercession rules
    base_path = Path( '/project' )
    supercession = cache.__.immut.Dictionary( {
        base_path: (
            frozenset( [ 'ignore/**' ] ),
            frozenset( [ 'protect/**' ] ),
        )
    } )
    cache_obj = cache.Cache(
        rules = { },
        defaults_disablement = frozenset( ),
        rules_supercession = supercession )

    # Test ignored path
    status = cache_obj.verify( base_path / 'ignore/file.txt' )
    assert not status.active

    # Test protected path
    status = cache_obj.verify( base_path / 'protect/file.txt' )
    assert status.active
    assert status.reason == core.Reasons.PlatformSensitive


def test_300_pattern_matching( ):
    ''' Pattern matching function works correctly. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    test_patterns = frozenset( [
        '**/*.secret',
        'protected/**',
        '**/sensitive/*',
    ] )

    # Test matching paths
    assert cache._check_path_patterns(
        Path( 'file.secret' ), test_patterns )
    assert cache._check_path_patterns(
        Path( 'some/path/file.secret' ), test_patterns )
    assert cache._check_path_patterns(
        Path( 'protected/file.txt' ), test_patterns )
    assert cache._check_path_patterns(
        Path( 'path/sensitive/file' ), test_patterns )

    # Test non-matching paths
    assert not cache._check_path_patterns(
        Path( 'file.txt' ), test_patterns )
    assert not cache._check_path_patterns(
        Path( 'unprotected/file.txt' ), test_patterns )
    assert not cache._check_path_patterns(
        Path( 'path/normal/file' ), test_patterns )


def test_400_from_configuration_basic( ):
    ''' Cache initializes from basic configuration. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    class MockAuxdata:
        ''' Mock auxdata for testing. '''
        def __init__( self ):
            self.configuration = { }
            self.directories = mock_directories = (
                type( 'MockDirectories', ( ), { } )( ) )
            mock_directories.user_config_path = '/test/config'

    auxdata = MockAuxdata( )
    cache_obj = cache.Cache.from_configuration( auxdata )

    # Should have some default rules (platform, credentials, etc.)
    assert cache_obj.rules
    assert cache_obj.defaults_disablement == frozenset( )
    assert cache_obj.rules_supercession == cache.__.immut.Dictionary( )


def test_410_from_configuration_custom_additions( ):
    ''' Cache processes custom locations and patterns. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    test_path = _nativize_path( '/custom/path' )
    config_path = _nativize_path( '/test/config' )

    test_config = {
        'protection': {
            'additional-locations': [ test_path ],
            'additional-patterns': [ '**/*.secret' ],
        }
    }

    class MockAuxdata:
        ''' Mock auxdata for testing. '''
        def __init__( self ):
            self.configuration = test_config
            self.directories = mock_directories = (
                type( 'MockDirectories', ( ), { } )( ) )
            mock_directories.user_config_path = config_path

    auxdata = MockAuxdata( )
    cache_obj = cache.Cache.from_configuration( auxdata )

    # Check custom additions are present
    custom_rule = cache_obj.rules[ core.Reasons.CustomAddition ]
    assert Path( test_path ) in custom_rule.paths
    assert '**/*.secret' in custom_rule.patterns


def test_420_from_configuration_defaults_disablement( ):
    ''' Cache processes defaults disablement configuration. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    test_config = {
        'protection': {
            'defaults-disablement': [ 'node_modules', '.git' ],
        }
    }

    class MockAuxdata:
        ''' Mock auxdata for testing. '''
        def __init__( self ):
            self.configuration = test_config
            self.directories = mock_directories = (
                type( 'MockDirectories', ( ), { } )( ) )
            mock_directories.user_config_path = '/test/config'

    auxdata = MockAuxdata( )
    cache_obj = cache.Cache.from_configuration( auxdata )

    assert 'node_modules' in cache_obj.defaults_disablement
    assert '.git' in cache_obj.defaults_disablement


def test_430_from_configuration_rules_supercession( ):
    ''' Cache processes rules supercession configuration. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    workspace_path = _nativize_path( '/workspace' )
    config_path = _nativize_path( '/test/config' )

    test_config = {
        'protection': {
            'rules-supercession': {
                workspace_path: {
                    'ignore': [ '.git', '.vscode' ],
                    'protect': [ '**/*secret*' ],
                }
            }
        }
    }

    class MockAuxdata:
        ''' Mock auxdata for testing. '''
        def __init__( self ):
            self.configuration = test_config
            self.directories = mock_directories = (
                type( 'MockDirectories', ( ), { } )( ) )
            mock_directories.user_config_path = config_path

    auxdata = MockAuxdata( )
    cache_obj = cache.Cache.from_configuration( auxdata )

    # Check supercession rules
    supercession = cache_obj.rules_supercession
    workspace_rules = supercession[ Path( workspace_path ) ]
    assert '.git' in workspace_rules[ 0 ]  # ignore patterns
    assert '.vscode' in workspace_rules[ 0 ]
    assert '**/*secret*' in workspace_rules[ 1 ]  # protect patterns


def test_440_provide_credentials_locations( ):
    ''' Cache includes credentials protection rules. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    rules = { }
    cache.provide_credentials_locations( rules )

    assert core.Reasons.Credentials in rules
    cred_rule = rules[ core.Reasons.Credentials ]

    # Should have paths relative to home directory
    home = Path.home( )
    assert any( path.is_relative_to( home ) for path in cred_rule.paths )


def test_450_provide_project_locations( ):
    ''' Cache includes project protection rules. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    rules = { }
    cache.provide_project_locations( rules )

    assert core.Reasons.Concealment in rules
    project_rule = rules[ core.Reasons.Concealment ]

    # Should have patterns for common project paths
    assert any( '**/.git/**' in pattern for pattern in project_rule.patterns )
    assert any(
        '**/.vscode/**' in pattern for pattern in project_rule.patterns )


def test_460_verify_supercession_non_relative( ):
    ''' Cache handles paths not relative to supercession roots. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    # Create cache with supercession rule for a specific directory
    rules = { }
    supercession = cache.__.immut.Dictionary( {
        Path( '/workspace' ): (
            frozenset( [ '.git' ] ),
            frozenset( [ '**/secret' ] ),
        )
    } )
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = supercession )

    # Test path completely unrelated to supercession root
    status = cache_obj.verify( Path( '/other/path/file.txt' ) )
    assert not status.active


def test_470_verify_supercession_unprotected( ):
    ''' Cache handles paths matching ignore but not protect patterns. '''
    cache = cache_import_module( f"{PACKAGE_NAME}.fsprotect.cache" )

    # Create cache with supercession rules
    rules = { }
    supercession = cache.__.immut.Dictionary( {
        Path( '/workspace' ): (
            frozenset( [ 'temp/**' ] ),
            frozenset( [ 'secret/**' ] ),
        )
    } )
    cache_obj = cache.Cache(
        rules = rules,
        defaults_disablement = frozenset( ),
        rules_supercession = supercession )

    # Test path under workspace that doesn't match protect patterns
    # but isn't explicitly ignored
    status = cache_obj.verify( Path( '/workspace/normal/file.txt' ) )
    assert not status.active
