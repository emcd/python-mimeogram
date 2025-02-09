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


''' Persistent and active process environment values. '''


from . import imports as __
from . import io as _io
from . import state as _state


_index_name = 'environment'


async def update( auxdata: _state.Globals ):
    ''' Updates process environment from dot files.

        For editable installations (development environments):
        - If project-level .env exists, use it exclusively.
        - Otherwise fall through to normal behavior.

        For normal installations:
        - Merge configured and local .env files.
        - Local values take precedence over configured values.
    '''
    if auxdata.distribution.editable:
        location = __.Path( auxdata.distribution.location ) / '.env'
        if location.exists( ):
            files = (
                location.glob( '*.env' )
                if location.is_dir( ) else ( location, ) )
            await _io.acquire_text_files_async(
                *( file for file in files ),
                deserializer = _inject_dotenv_data )
            return
    locations: list[ __.Path ] = [ ]
    template = auxdata.configuration.get( 'locations', { } ).get( _index_name )
    if template:
        location = __.Path( template.format(
            user_configuration = auxdata.directories.user_config_path,
            user_home = __.Path.home( ) ) )
        if location.exists( ): locations.append( location )
    location = __.Path( ) / '.env'
    if location.exists( ): locations.append( location )
    # Process locations in reverse precedence order.
    for location in reversed( locations ):
        files = (
            location.glob( '*.env' )
            if location.is_dir( ) else ( location, ) )
        await _io.acquire_text_files_async(
            *( file for file in files ),
            deserializer = _inject_dotenv_data )


def _inject_dotenv_data( data: str ) -> bool:
    from io import StringIO
    from dotenv import load_dotenv
    return load_dotenv( stream = StringIO( data ) )
