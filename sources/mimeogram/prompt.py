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


from __future__ import annotations

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


class Command(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Provides LLM prompt text for mimeogram format. '''

    clip: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--clipboard', '--to-clipboard' ),
            help = "Copy prompt to clipboard." ),
    ] = False

    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command to provide prompt text. '''
        await provide_prompt( auxdata, self )


async def acquire_prompt( auxdata: __.Globals ) -> str:
    ''' Acquires prompt text from package data. '''
    location = (
        auxdata.distribution.provide_data_location(
            'prompts', 'mimeogram.md' ) )
    return await __.acquire_text_file_async( location )


async def provide_prompt( auxdata: __.Globals, cmd: Command ) -> None:
    ''' Provides mimeogram prompt text. '''
    try: prompt = await acquire_prompt( auxdata )
    except Exception as exc:
        _scribe.exception( "Could not acquire prompt text." )
        raise SystemExit( 1 ) from exc
    if cmd.clip:
        try: _pyperclip.copy( prompt )
        except Exception as exc:
            _scribe.exception( "Could not copy prompt to clipboard." )
            raise SystemExit( 1 ) from exc
        _scribe.info( "Copied prompt to clipboard." )
    else: print( prompt )
    raise SystemExit( 0 )
