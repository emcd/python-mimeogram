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


''' Fundamental configuration. '''


from . import imports as __
from . import dictedits as _dictedits
from . import distribution as _distribution
from . import exceptions as _exceptions
from . import io as _io


class EnablementTristate( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Disable, enable, or retain the natural state? '''

    Disable = 'disable'
    Retain = 'retain'
    Enable = 'enable'

    def __bool__( self ) -> bool:
        if self.Disable is self: return False
        if self.Enable is self: return True
        raise _exceptions.OperationInvalidity(
            'inert enablement tristate', 'boolean translation' )

    def is_retain( self ) -> bool:
        ''' Does enum indicate a retain state? '''
        return self.Retain is self


async def acquire(
    application_name: str,
    directories: __.PlatformDirs,
    distribution: _distribution.Information,
    edits: _dictedits.Edits = ( ),
    file: __.Absential[ __.Path ] = __.absent,
) -> __.AccretiveDictionary[ str, __.typx.Any ]:
    ''' Loads configuration as dictionary. '''
    if __.is_absent( file ):
        file = _discover_copy_template( directories, distribution )
    configuration = await _acquire( file )
    includes = await _acquire_includes(
        application_name, directories, configuration.get( 'includes', ( ) ) )
    for include in includes: configuration.update( include )
    for edit in edits: edit( configuration )
    return __.AccretiveDictionary( configuration )


async def _acquire( file: __.Path ) -> __.NominativeDictionary:
    from aiofiles import open as open_
    from tomli import loads
    async with open_( file ) as stream:
        return loads( await stream.read( ) )


async def _acquire_includes(
    application_name: str,
    directories: __.PlatformDirs,
    specs: tuple[ str, ... ]
) -> __.cabc.Sequence[ dict[ str, __.typx.Any ] ]:
    from itertools import chain
    from tomli import loads
    locations = tuple(
        __.Path( spec.format(
            user_configuration = directories.user_config_path,
            user_home = __.Path.home( ),
            application_name = application_name ) )
        for spec in specs )
    iterables = tuple(
        ( location.glob( '*.toml' ) if location.is_dir( ) else ( location, ) )
        for location in locations )
    return await _io.acquire_text_files_async(
        *( file for file in chain.from_iterable( iterables ) ),
        deserializer = loads )


def _discover_copy_template(
    directories: __.PlatformDirs, distribution: _distribution.Information
) -> __.Path:
    from shutil import copyfile
    file = directories.user_config_path / 'general.toml'
    if not file.exists( ):
        copyfile(
            distribution.provide_data_location(
                'configuration', 'general.toml' ), file )
    return file
