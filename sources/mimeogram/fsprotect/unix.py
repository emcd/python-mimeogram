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


''' Sensitive filesystem locations on Unix/POSIX/Linux. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


def discover_system_paths( ) -> frozenset[ __.Path ]:
    ''' Discovers Unix and other relevant system paths. '''
    paths: set[ __.Path ] = set( )
    paths.update( map(
        __.Path,
        (   '/bin', '/boot', '/dev', '/etc', '/opt',
            '/proc', '/sbin', '/sys', '/usr',
        ) ) )
    #if _detect_wsl( ): paths.update( _discover_wsl_system_paths( ) )
    return frozenset( paths )


# def _detect_wsl( ) -> bool:
#     ''' Checks if running in WSL environment. '''
#     # TODO: If environment vars are not set, then return False.
#     #       Else, proceed to more expensive check to ensure sane WSL.
#     wsl_vars = ( 'WSL_DISTRO_NAME', 'WSL_INTEROP' )
#     for var in wsl_vars:
#         if __.os.environ.get( var ):
#             _scribe.debug( f"WSL detected via {var} environment variable" )
#             return True
#     try:
#         with open( '/proc/version', 'r' ) as f: # pylint: disable=unspecified-encoding
#             version_info = f.read( ).lower( )
#     except Exception as exc: # pylint: disable=broad-exception-caught
#         _scribe.debug( f"Error checking /proc/version: {exc}" )
#     if 'microsoft' in version_info: # pylint: disable=magic-value-comparison
#         _scribe.debug( "WSL detected via /proc/version" )
#         return True
#     if 'microsoft' in __.os.uname( ).release.lower( ): # pylint: disable=magic-value-comparison
#         _scribe.debug( "WSL detected via kernel release string." )
#         return True
#     return False


# def _discover_wsl_system_paths( ) -> set[ __.Path ]:
#     # TODO: Better method to determine Windows syspaths from WSL.
#     #       Possibly like https://stackoverflow.com/a/55635008/14833542
#     #       since the proper ones cannot be guaranteed via 'WSLENV'.
#     #       But, running 'cmd' is expensive.
#     from . import windows
#     paths = windows.discover_system_paths( )
#     paths_: set[ __.Path ] = set( )
#     for path in paths:
#         parts = path.parts
#         if 1 >= len( parts ): continue
#         drive = parts[ 0 ][ 0 ].lower( ) # TODO? Consider UNC paths.
#         paths_.add( __.Path( f"/mnt/{drive}" ).joinpath( *parts[ 1 : ] ) )
#     _scribe.debug( "Calculated {} WSL system paths.".format( len( paths_ ) ) )
#     return paths_
