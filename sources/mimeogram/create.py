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
from . import tokenizers as _tokenizers


_scribe = __.produce_scribe( __name__ )


class Command(
    _interfaces.CliCommand,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Creates mimeogram from filesystem locations or URLs. '''

    sources: __.typx.Annotated[
        __.tyro.conf.Positional[ list[ str ] ],
        __.typx.Doc( ''' Filesystem locations or URLs. ''' ),
        __.tyro.conf.arg( prefix_name = False ),
    ]
    clip: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc( ''' Copy mimeogram to clipboard. ''' ),
        __.tyro.conf.arg( aliases = ( '--clipboard', '--to-clipboard' ) ),
    ] = None
    count_tokens: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc( ''' Count total tokens in mimeogram. ''' ),
    ] = None
    edit: __.typx.Annotated[
        bool,
        __.typx.Doc( ''' Spawn editor to capture introductory message. ''' ),
        __.tyro.conf.arg( aliases = ( '-e', '--edit-message' ) ),
    ] = False
    prepend_prompt: __.typx.Annotated[
        bool,
        __.typx.Doc( ''' Prepend mimeogram format instructions. ''' ),
    ] = False
    recurse: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc( ''' Recurse into directories. ''' ),
        __.tyro.conf.arg(
            aliases = ( '-r', '--recurse-directories', '--recursive' ) ),
    ] = None
    strict: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Fail on invalid contents? True, fail. False, skip. ''' ),
        __.tyro.conf.arg( aliases = ( '--fail-on-invalid', ) ),
    ] = None
    tokenizer: __.typx.Annotated[
        __.typx.Optional[ _tokenizers.Tokenizers ],
        __.typx.Doc( ''' Which tokenizer to use for counting? ''' ),
    ] = None
    tokenizer_variant: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc(
            ''' Which tokenizer variant to use for counting?

                'tiktoken': 'cl100k_base', 'o200k_base', etc....

                Not all tokenizers have variants.
                If not specified, then the default variant is used.
            ''' ),
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
        if None is not self.count_tokens:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'create', 'count-tokens' ),
                value = self.count_tokens ) )
        if None is not self.recurse:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'acquire-parts', 'recurse-directories' ),
                value = self.recurse ) )
        if None is not self.strict:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'acquire-parts', 'fail-on-invalid' ),
                value = self.strict ) )
        if None is not self.tokenizer:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'tokenizers', 'default' ),
                value = self.tokenizer ) )
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


async def create(
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
    if options.get( 'count-tokens', False ):
        with __.report_exceptions(
            _scribe, "Could not count mimeogram tokens."
        ):
            tokenizer = await _tokenizer_from_command( auxdata, command )
            tokens_count = await tokenizer.count( mimeogram )
            _scribe.info( f"Total mimeogram size is {tokens_count} tokens." )
    if options.get( 'to-clipboard', False ):
        with __.report_exceptions(
            _scribe, "Could not copy mimeogram to clipboard."
        ): await clipcopier( mimeogram )
    else: print( mimeogram ) # TODO? Use output stream from configuration.
    raise SystemExit( 0 )


async def _tokenizer_from_command(
    auxdata: __.Globals, command: Command
) -> _tokenizers.Tokenizer:
    options = auxdata.configuration.get( 'tokenizers', { } )
    name = (
        command.tokenizer.value if command.tokenizer
        else options.get( 'default', 'tiktoken' ) )
    variant = command.tokenizer_variant
    args = dict( variant = variant ) if variant else { }
    return await _tokenizers.Tokenizers.produce( name, **args )
