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


''' Mimeogram prompt text for LLMs. '''
# TODO? Use BSD sysexits.


from __future__ import annotations

from . import __
from . import interfaces as _interfaces


_scribe = __.produce_scribe( __name__ )


class Command(
    _interfaces.CliCommand,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Provides LLM prompt text for mimeogram format. '''

    clip: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            aliases = ( '--clipboard', '--to-clipboard' ),
            help = "Copy prompt to clipboard." ),
    ] = None

    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command to provide prompt text. '''
        await provide_prompt( auxdata )

    def provide_configuration_edits( self ) -> __.DictionaryEdits:
        ''' Provides edits against configuration from options. '''
        edits: list[ __.DictionaryEdit ] = [ ]
        if None is not self.clip:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'prompt', 'to-clipboard' ), value = self.clip ) )
        return tuple( edits )


async def acquire_prompt( auxdata: __.Globals ) -> str:
    ''' Acquires prompt text from package data. '''
    location = (
        auxdata.distribution.provide_data_location(
            'prompts', 'mimeogram.md' ) )
    return await __.acquire_text_file_async( location )


async def provide_prompt( auxdata: __.Globals ) -> None:
    ''' Provides mimeogram prompt text. '''
    with __.report_exceptions( _scribe, "Could not acquire prompt text." ):
        prompt = await acquire_prompt( auxdata )
    options = auxdata.configuration.get( 'prompt', { } )
    if options.get( 'to-clipboard', False ):
        from pyperclip import copy
        with __.report_exceptions(
            _scribe, "Could not copy prompt to clipboard."
        ): copy( prompt )
        _scribe.info( "Copied prompt to clipboard." )
    else: print( prompt ) # TODO? Use output stream from configuration.
    raise SystemExit( 0 )
