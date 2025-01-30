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


''' Sensitive filesystem locations on Windows. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


CSIDL_PROGRAM_FILES_COMMON = 0x002b    # C:\Program Files\Common Files
CSIDL_PROGRAM_FILES_COMMONX86 = 0x002c # C:\Program Files (x86)\Common Files


def discover_system_paths( ) -> frozenset[ __.Path ]:
    ''' Discovers system paths via standard Windows mechanisms. '''
    paths: set[ __.Path ] = set( )
    paths.update( _discover_system_paths_via_environment( ) )
    paths.update( _discover_system_paths_via_api( ) )
    # TODO? Cygwin
    if _detect_mingw( ): _discover_add_mingw_system_paths( paths )
    return frozenset( paths )


def _detect_mingw( ) -> bool:
    ''' Checks if running in MinGW environment. '''
    # TODO: If environment vars are not set, then return False.
    #       Else, proceed to more expensive checck to ensure sane MinGW.
    mingw_env = __.os.environ.get( 'MSYSTEM', '' )
    if mingw_env.startswith( ('MINGW', 'MSYS') ):
        _scribe.debug( f'MinGW detected via MSYSTEM={mingw_env}' )
        return True
    mingw_paths = ( '/mingw32', '/mingw64', '/msys', '/usr/bin/msys-2.0.dll' )
    for path in mingw_paths:
        if not __.Path( path ).exists( ): continue
        _scribe.debug( f'MinGW detected via path: {path}' )
        return True
    return False


def _discover_add_mingw_system_paths( paths: set[ __.Path ] ) -> None:
    paths_: set[ __.Path ] = set( )
    for path in paths:
        parts = path.parts
        if 1 >= len( parts ): continue
        drive = parts[ 0 ][ 0 ].lower( ) # TODO? Consider UNC paths.
        paths_.add( __.Path( f"/{drive}" ).joinpath( *parts[ 1 : ] ) )
    _scribe.debug(
        "Calculated {} MingGW system paths.".format( len( paths_ ) ) )
    paths_.update( map(
        __.Path,
        (   '/bin', '/dev', '/etc',
            '/mingw32', '/mingw64', '/msys', '/proc', '/usr',
        ) ) )
    paths.update( paths_ )


def _discover_system_paths_via_environment( ) -> frozenset[ __.Path ]:
    ''' Discovers system paths via environment. '''
    environ = __.os.environ
    paths: set[ __.Path ] = set( )
    system_drive = environ.get( 'SystemDrive', 'C:' )
    system_root = environ.get( 'SystemRoot', f"{system_drive}\\Windows" )
    paths.add( __.Path( system_root ) )
    paths.add( __.Path( f"{system_drive}/System Volume Information" ) )
    # Program Files variations
    progfiles = __.os.environ.get(
        'ProgramFiles', f"{system_drive}\\Program Files" )
    paths.add( __.Path( progfiles ) )
    for progfiles_ename in (
        'ProgramFiles(x86)', 'ProgramFiles(Arm)', 'ProgramW6432'
    ):
        progfiles = environ.get( progfiles_ename )
        if progfiles: paths.add( __.Path( progfiles ) )
    return frozenset( paths )


def _discover_system_paths_via_api( ) -> set[ __.Path ]:
    ''' Discovers system paths via API. '''
    import ctypes
    from ctypes.wintypes import MAX_PATH
    dmessage = "Could not retrieve additional Windows system paths via API."
    paths: set[ __.Path ] = set( )
    try: dll = ctypes.windll.shell32 # pyright: ignore
    except Exception: # pylint: disable=broad-exception-caught
        _scribe.debug( dmessage )
    buf = ctypes.create_unicode_buffer( MAX_PATH + 1 )
    for key in (
        CSIDL_PROGRAM_FILES_COMMON,
        CSIDL_PROGRAM_FILES_COMMONX86,
    ):
        try:
            dll.SHGetFolderPathW( # pyright: ignore
                None, key, None, 0, buf )
            paths.add( __.Path( buf.value ) )
        except Exception: # pylint: disable=broad-exception-caught
            _scribe.debug( dmessage )
    return paths


def discover_user_paths( ) -> frozenset[ __.Path ]:
    ''' Discovers Windows user-specific paths that should be protected. '''
    paths: set[ __.Path ] = set( )
    appdata = __.os.environ.get( 'APPDATA' )
    local_appdata = __.os.environ.get( 'LOCALAPPDATA' )
    userprofile = __.os.environ.get( 'USERPROFILE' )
    if appdata: paths.add( __.Path( appdata ) )
    if local_appdata: paths.add( __.Path( local_appdata ) )
    if userprofile:
        profile = __.Path( userprofile )
        paths.update( (
            profile / 'AppData' / 'Local',
            profile / 'AppData' / 'LocalLow',
            profile / 'AppData' / 'Roaming',
            # Legacy Paths
            profile / 'Application Data',
            profile / 'Local Settings',
        ) )
    return frozenset( paths )
