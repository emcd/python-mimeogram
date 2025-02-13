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


_scribe = __.produce_scribe( __name__ )


class Command(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Creates mimeogram from filesystem locations or URLs. '''
    # TODO: Inherit from abstract command.

    sources: __.typx.Annotated[
        __.tyro.conf.Positional[ list[ str ] ],
        __.tyro.conf.arg( # pyright: ignore
            help = "Filesystem locations or URLs.",
            prefix_name = False ),
    ]
    clip: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--clipboard', '--to-clipboard' ),
            help = "Copy mimeogram to clipboard." ),
    ] = None
    edit: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '-e', '--edit-message' ),
            help = "Spawn editor to capture an introductory message." ),
    ] = False
    prepend_prompt: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            help = "Prepend mimeogram format instructions." ),
    ] = False
    recurse: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '-r', '--recurse-directories', '--recursive' ),
            help = "Recurse into directories." ),
    ] = None
    strict: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg( # pyright: ignore
            help = "Fail on invalid contents instead of skipping them." ),
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
    try: copy( mimeogram )
    except Exception as exc:
        _scribe.exception( "Could not copy mimeogram to clipboard." )
        raise SystemExit( 1 ) from exc
    _scribe.info( "Copied mimeogram to clipboard." )


async def _edit_message( ) -> str:
    from .edit import edit_content
    try: return edit_content( )
    except Exception as exc:
        _scribe.exception( "Could not acquire user message." )
        raise SystemExit( 1 ) from exc


async def create( # pylint: disable=too-many-locals
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
    if command.edit:
        try: message = await editor( )
        except Exception as exc:
            _scribe.exception( "Could not acquire user message." )
            raise SystemExit( 1 ) from exc
    else: message = None
    try: parts = await acquire( auxdata, command.sources )
    except Exception as exc:
        _scribe.exception( "Could not acquire mimeogram parts." )
        raise SystemExit( 1 ) from exc
    mimeogram = format_mimeogram( parts, message = message )
    # TODO? Pass prompt to 'format_mimeogram'.
    if command.prepend_prompt:
        prompt = await prompter( auxdata )
        mimeogram = f"{prompt}\n\n{mimeogram}"
    options = auxdata.configuration.get( 'create', { } )
    if options.get( 'to-clipboard', False ):
        try: await clipcopier( mimeogram )
        except Exception as exc:
            _scribe.exception( "Could not copy mimeogram to clipboard." )
            raise SystemExit( 1 ) from exc
    else: print( mimeogram ) # TODO? Use output stream from configuration.
    raise SystemExit( 0 )
