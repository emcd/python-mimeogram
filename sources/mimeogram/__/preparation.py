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


''' Preparation of the library core. '''


from . import imports as __
from . import application as _application
from . import configuration as _configuration
from . import dictedits as _dictedits
from . import distribution as _distribution
from . import environment as _environment
from . import inscription as _inscription
from . import state as _state


async def prepare( # pylint: disable=too-many-arguments,too-many-locals
    exits: __.ExitsAsync,
    application: _application.Information = _application.Information( ),
    configedits: _dictedits.Edits = ( ),
    configfile: __.Absential[ __.Path ] = __.absent,
    environment: bool = False,
    inscription: __.Absential[ _inscription.Control ] = __.absent,
) -> _state.Globals:
    ''' Prepares globals DTO for use with library functions.

        Also:
        * Configures logging for library package (not application).
        * Optionally, loads process environment from files.

        Note that asynchronous preparation allows for applications to
        concurrently initialize other entities outside of the library, even
        though the library initialization, itself, is inherently sequential.
    '''
    directories = application.produce_platform_directories( )
    distribution = (
        await _distribution.Information.prepare(
            package = __.package_name, exits = exits ) )
    configuration = (
        await _configuration.acquire(
            application_name = application.name,
            directories = directories,
            distribution = distribution,
            edits = configedits,
            file = configfile ) )
    auxdata = _state.Globals(
        application = application,
        configuration = configuration,
        directories = directories,
        distribution = distribution,
        exits = exits )
    if environment: await _environment.update( auxdata )
    if __.is_absent( inscription ):
        inscription_: _inscription.Control = _inscription.Control( )
    else: inscription_ = inscription
    _inscription.prepare( control = inscription_ )
    _inscribe_preparation_report( auxdata )
    return auxdata


def _inscribe_preparation_report( auxdata: _state.Globals ):
    scribe = __.produce_scribe( __.package_name )
    scribe.debug( f"Application Name: {auxdata.application.name}" )
    # scribe.debug( f"Execution ID: {auxdata.application.execution_id}" )
    scribe.debug( "Application Cache Location: {}".format(
        auxdata.provide_cache_location( ) ) )
    scribe.debug( "Application Data Location: {}".format(
        auxdata.provide_data_location( ) ) )
    scribe.debug( "Application State Location: {}".format(
        auxdata.provide_state_location( ) ) )
    scribe.debug( "Package Data Location: {}".format(
        auxdata.distribution.provide_data_location( ) ) )
