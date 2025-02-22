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


''' Creation of mimeograms. '''
# TODO? Use BSD sysexits.


from __future__ import annotations

from . import __
from . import interfaces as _interfaces


_scribe = __.produce_scribe( __name__ )


class Command(
    _interfaces.CliCommand,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Creates mimeogram from filesystem locations or URLs. '''

    sources: __.typx.Annotated[
        __.tyro.conf.Positional[ list[ str ] ],
        __.tyro.conf.arg(
            help = "Filesystem locations or URLs.",
            prefix_name = False ),
    ]
    clip: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            aliases = ( '--clipboard', '--to-clipboard' ),
            help = "Copy mimeogram to clipboard." ),
    ] = None
    edit: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            aliases = ( '-e', '--edit-message' ),
            help = "Spawn editor to capture an introductory message." ),
    ] = False
    prepend_prompt: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Prepend mimeogram format instructions." ),
    ] = False
    recurse: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            aliases = ( '-r', '--recurse-directories', '--recursive' ),
            help = "Recurse into directories." ),
    ] = None
    strict: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            aliases = ( '--fail-on-invalid', ),
            help = "Fail on invalid contents? True, fail. False, skip." ),
    ] = None

    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command to create mimeogram. '''
        await create( auxdata, self )

    def provide_configuration_edits( self ) -> __.DictionaryEdits:
        ''' Provides edits against configuration from options. '''
        edits: list[ __.DictionaryEdit ] = [ ]
        if None is not self.clip:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'create', 'to-clipboard' ), value = self.clip ) )
        if None is not self.recurse:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'acquire-parts', 'recurse-directories' ),
                value = self.recurse ) )
        if None is not self.strict:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'acquire-parts', 'fail-on-invalid' ),
                value = self.strict ) )
        return tuple( edits )


async def _acquire_prompt( auxdata: __.Globals ) -> str:
    from .prompt import acquire_prompt
    return await acquire_prompt( auxdata )


async def _copy_to_clipboard( mimeogram: str ) -> None:
    from pyperclip import copy
    copy( mimeogram )
    _scribe.info( "Copied mimeogram to clipboard." )


async def _edit_message( ) -> str:
    from .edit import edit_content
    return edit_content( )


async def create( # pylint: disable=too-complex,too-many-locals
    auxdata: __.Globals,
    command: Command, *,
    editor: __.cabc.Callable[
        [ ], __.cabc.Coroutine[ None, None, str ] ] = _edit_message,
    clipcopier: __.cabc.Callable[
        [ str ], __.cabc.Coroutine[ None, None, None ] ] = _copy_to_clipboard,
    prompter: __.cabc.Callable[
        [ __.Globals ],
        __.cabc.Coroutine[ None, None, str ] ] = _acquire_prompt,
) -> __.typx.Never:
    ''' Creates mimeogram. '''
    from .acquirers import acquire
    from .formatters import format_mimeogram
    with __.report_exceptions(
        _scribe, "Could not acquire mimeogram parts."
    ): parts = await acquire( auxdata, command.sources )
    if command.edit:
        with __.report_exceptions(
            _scribe, "Could not acquire user message."
        ): message = await editor( )
    else: message = None
    mimeogram = format_mimeogram( parts, message = message )
    # TODO? Pass prompt to 'format_mimeogram'.
    if command.prepend_prompt:
        prompt = await prompter( auxdata )
        mimeogram = f"{prompt}\n\n{mimeogram}"
    options = auxdata.configuration.get( 'create', { } )
    if options.get( 'to-clipboard', False ):
        with __.report_exceptions(
            _scribe, "Could not copy mimeogram to clipboard."
        ): await clipcopier( mimeogram )
    else: print( mimeogram ) # TODO? Use output stream from configuration.
    raise SystemExit( 0 )
