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


''' Cache for filesystem protection checks. '''


from __future__ import annotations

from . import __
from . import core as _core


_scribe = __.produce_scribe( __name__ )


class Rule(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Rule for path protection. '''

    paths: frozenset[ __.Path ]
    patterns: frozenset[ str ] = frozenset( )


class Cache( _core.Protector, decorators = ( __.standard_dataclass, ) ):
    ''' Cache of protected paths and patterns for platform. '''

    rules: dict[ _core.Reasons, Rule ]
    defaults_disablement: frozenset[ str ]
    rules_supercession: __.ImmutableDictionary[
        __.Path, tuple[ frozenset[ str ], frozenset[ str ] ] ]

    @classmethod
    def from_configuration( selfclass, auxdata: __.Globals ) -> Cache:
        ''' Initializes protection cache for current platform. '''
        _scribe.debug( 'Initializing protection cache.' )
        rules: dict[ _core.Reasons, Rule ] = { }
        discover_platform_locations( auxdata, rules )
        provide_credentials_locations( rules )
        provide_project_locations( rules )
        disables, supercedes = _process_configuration( auxdata, rules )
        return selfclass(
            rules = rules,
            defaults_disablement = disables,
            rules_supercession = supercedes )

    def verify( self, path: __.Path ) -> _core.Status: # pylint: disable=too-many-locals
        ''' Verifies if a path should be protected using cached data. '''
        path = _normalize_path( path )
        _scribe.debug( f"Path: {path}" )

        if any( part in self.defaults_disablement for part in path.parts ):
            return _core.Status( path = path, active = False )

        for dir_path, ( ignore, protect ) in self.rules_supercession.items( ):
            dir_path_ = _normalize_path( dir_path )
            if not path.is_relative_to( dir_path_ ): continue
            rel_path = path.relative_to( dir_path_ )
            if _check_path_patterns( rel_path, ignore ):
                return _core.Status( path = path, active = False )
            if _check_path_patterns( rel_path, protect ):
                return _core.Status(
                    path = path,
                    reason = _core.Reasons.PlatformSensitive,
                    active = True )

        for reason, rule in self.rules.items( ):
            for protected_path in rule.paths:
                protected_path_ = _normalize_path( protected_path )
                if path.is_relative_to( protected_path_ ):
                    return _core.Status(
                        path = path,
                        reason = reason,
                        active = True )
            if _check_path_patterns( path, rule.patterns ):
                return _core.Status(
                    path = path,
                    reason = reason,
                    active = True )

        return _core.Status( path = path, active = False )


def provide_credentials_locations(
    rules: dict[ _core.Reasons, Rule ]
) -> None:
    ''' Provides common locations for credentials and other secrets. '''
    from . import home as module
    home = __.Path.home( )
    cred_paths = {
        home / path for path in module.discover_sensitive_locations( ) }
    rules[ _core.Reasons.Credentials ] = Rule(
        paths = frozenset( cred_paths ) )


def provide_project_locations(
    rules: dict[ _core.Reasons, Rule ]
) -> None:
    ''' Provides IDE and VCS locations relative to project. '''
    from . import project as module
    project_sensitive = module.discover_sensitive_locations( )
    # TODO: Consider whether these patterns are compatible with Windows.
    rules[ _core.Reasons.Concealment ] = Rule(
        paths = frozenset( ),
        patterns = frozenset(
            f"**/{path}/**" for path in project_sensitive ) )


def _check_path_patterns( path: __.Path, patterns: frozenset[ str ] ) -> bool:
    ''' Checks if path matches any of the glob patterns. '''
    from wcmatch import glob
    str_path = str( path )
    return glob.globmatch( str_path, list( patterns ), flags = glob.GLOBSTAR )


def discover_platform_locations(
    auxdata: __.Globals, rules: dict[ _core.Reasons, Rule ]
) -> None:
    ''' Discovers system and user locations based on platform. '''
    match __.sys.platform:
        case 'darwin':
            from . import macos as module
            sys_paths = module.discover_system_paths( )
            user_paths = module.discover_user_paths( )
        case 'win32':
            from . import windows as module
            sys_paths = module.discover_system_paths( )
            user_paths = module.discover_user_paths( )
        case _:
            from . import unix as module
            sys_paths = module.discover_system_paths( )
            user_paths: frozenset[ __.Path ] = frozenset( )
    rules[ _core.Reasons.OsDirectory ] = Rule( paths = frozenset( sys_paths ) )
    config_paths = (
        user_paths | { __.Path( auxdata.directories.user_config_path ), } )
    rules[ _core.Reasons.UserConfiguration ] = Rule(
        paths = frozenset( config_paths ) )


def _expand_location( path: str ) -> __.Path:
    ''' Expands path with home directory and environment variables. '''
    expanded = __.os.path.expanduser( __.os.path.expandvars( path ) )
    if (    __.sys.platform == 'win32' # pylint: disable=magic-value-comparison
            and expanded.startswith( '/' )
            and not expanded.startswith( '//' ) # Skip UNC paths
    ):
        expanded = expanded.lstrip( '/' )
        path_obj = __.Path( expanded )
        if not path_obj.is_absolute( ):
            path_obj = __.Path( __.Path.cwd( ).drive + '/' + expanded )
    else: path_obj = __.Path( expanded )
    return _normalize_path( path_obj.resolve( ) )


def _normalize_path( path: __.Path ) -> __.Path:
    ''' Normalizes path for consistent comparison across platforms. '''
    resolved = path.resolve( )
    if __.sys.platform == 'win32' and resolved.drive: # pylint: disable=magic-value-comparison
        return __.Path(
            resolved.drive.lower( )
            + str( resolved )[ len( resolved.drive ): ] )
    return resolved


def _process_configuration(
    auxdata: __.Globals,
    rules: dict[ _core.Reasons, Rule ],
) -> tuple[
    frozenset[ str ],
    __.ImmutableDictionary[
        __.Path, tuple[ frozenset[ str ], frozenset[ str ] ] ],
]:
    config = auxdata.configuration.get( 'protection', { } )
    if not config: return frozenset( ), __.ImmutableDictionary( )
    # Additional locations and patterns.
    locations_add = {
        _expand_location( path )
        for path in config.get( 'additional-locations', ( ) ) }
    patterns_add = set( config.get( 'additional-patterns', ( ) ) )
    rules[ _core.Reasons.CustomAddition ] = Rule(
        paths = frozenset( locations_add ),
        patterns = frozenset( patterns_add ) )
    # Override defaults.
    patterns_remove = frozenset( config.get( 'defaults-disablement', ( ) ) )
    # Process directory overrides
    supercession_rules: dict[
        __.Path, tuple[ frozenset[ str ], frozenset[ str ] ] ] = { }
    for dir_path, dir_rules in config.get(
        'rules-supercession', { }
    ).items( ):
        full_path = _expand_location( dir_path )
        supercession_rules[ full_path ] = (
            frozenset( dir_rules.get( 'ignore', [ ] ) ),
            frozenset( dir_rules.get( 'protect', [ ] ) ) )
    return patterns_remove, __.ImmutableDictionary( supercession_rules )
