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


''' Application of mimeograms. '''
# TODO? Use BSD sysexits.


from __future__ import annotations

from . import __
from . import interfaces as _interfaces
from . import parts as _parts
from . import updaters as _updaters


_scribe = __.produce_scribe( __name__ )


class Command(
    _interfaces.CliCommand,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Applies mimeogram to filesystem locations. '''

    source: __.typx.Annotated[
        str, # TODO: str | Path
        __.tyro.conf.arg(
            help = (
                "Source file for mimeogram. "
                "Defaults to stdin if '--clip' not specified." ) ),
    ] = '-'
    clip: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            aliases = ( '--clipboard', '--from-clipboard' ),
            help = "Read mimeogram from clipboard instead of file or stdin." ),
    ] = None
    mode: __.typx.Annotated[
        __.typx.Optional[ _updaters.ReviewModes ],
        __.tyro.conf.arg(
            aliases = ( '--review-mode', ),
            help = (
                "Controls how changes are reviewed. "
                "'silent': Apply without review. "
                "'partitive': Review each change interactively. "
                "Partitive, if not specified and on a terminal. "
                "Silent, if not specified and not on a terminal." ) ),
    ] = None
    base: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg(
            aliases = ( '--base-directory', ),
            help = (
                "Base directory for relative locations. "
                "Defaults to current working directory." ) ),
    ] = None
    force: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.tyro.conf.arg(
            help = 'Override protected path checks.' ),
    ] = None

    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command to apply mimeogram. '''
        await apply( auxdata, self )

    def provide_configuration_edits( self ) -> __.DictionaryEdits:
        ''' Provides edits against configuration from options. '''
        edits: list[ __.DictionaryEdit ] = [ ]
        if None is not self.clip:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'apply', 'from-clipboard' ), value = self.clip ) )
        if None is not self.force:
            edits.append( __.SimpleDictionaryEdit( # pyright: ignore
                address = ( 'update-parts', 'disable-protections' ),
                value = self.force ) )
        return tuple( edits )


class ContentAcquirer( # pylint: disable=invalid-metaclass
    __.typx.Protocol,
    metaclass = __.ImmutableStandardProtocolDataclass,
    decorators = ( __.standard_dataclass, __.typx.runtime_checkable ),
):
    ''' Acquires content for apply command. '''

    @__.abc.abstractmethod
    def stdin_is_tty( self ) -> bool:
        ''' Checks if input is from a terminal. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    async def acquire_clipboard( self ) -> str:
        ''' Acquires content from clipboard. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    async def acquire_file( self, path: str | __.Path ) -> str:
        ''' Acquires content from file. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    async def acquire_stdin( self ) -> str:
        ''' Acquires content from standard input. '''
        raise NotImplementedError


class StandardContentAcquirer(
    ContentAcquirer, decorators = ( __.standard_dataclass, )
):
    ''' Standard implementation of content acquisition. '''

    def stdin_is_tty( self ) -> bool:
        return __.sys.stdin.isatty( )

    async def acquire_clipboard( self ) -> str:
        from pyperclip import paste
        return paste( )

    async def acquire_file( self, path: str | __.Path ) -> str:
        return await __.acquire_text_file_async( path )

    async def acquire_stdin( self ) -> str:
        return __.sys.stdin.read( )


async def apply( # pylint: disable=too-complex
    auxdata: __.Globals,
    command: Command,
    *,
    acquirer: __.Absential[ ContentAcquirer ] = __.absent,
    parser: __.Absential[
        __.cabc.Callable[ [ str ], __.cabc.Sequence[ _parts.Part ] ]
    ] = __.absent,
    updater: __.Absential[
        __.cabc.Callable[
            [   __.Globals,
                __.cabc.Sequence[ _parts.Part ],
                _updaters.ReviewModes ],
            __.cabc.Coroutine[ None, None, None ]
        ]
    ] = __.absent,
) -> __.typx.Never:
    ''' Applies mimeogram. '''
    if __.is_absent( acquirer ):
        acquirer = StandardContentAcquirer( )
    if __.is_absent( parser ):
        from .parsers import parse as parser
    if __.is_absent( updater ):
        from .updaters import update as updater
    review_mode = _determine_review_mode( command, acquirer )
    with __.report_exceptions(
        _scribe, "Could not acquire mimeogram to apply."
    ): mgtext = await _acquire( auxdata, command, acquirer )
    if not mgtext:
        _scribe.error( "Cannot apply empty mimeogram." )
        raise SystemExit( 1 )
    with __.report_exceptions( _scribe, "Could not parse mimeogram." ):
        parts = parser( mgtext )
    nomargs: dict[ str, __.typx.Any ] = { }
    if command.base: nomargs[ 'base' ] = command.base
    with __.report_exceptions( _scribe, "Could not apply mimeogram." ):
        await updater( auxdata, parts, review_mode, **nomargs )
    # TODO: If all parts ignored or inapplicable, then do not mention success.
    _scribe.info( "Successfully applied mimeogram" )
    raise SystemExit( 0 )


async def _acquire(
    auxdata: __.Globals, cmd: Command, acquirer: ContentAcquirer
) -> str:
    ''' Acquires content to parse from clipboard, file, or stdin. '''
    options = auxdata.configuration.get( 'apply', { } )
    if options.get( 'from-clipboard', False ):
        content = await acquirer.acquire_clipboard( )
        if not content:
            _scribe.error( "Clipboard is empty." )
            raise SystemExit( 1 )
        _scribe.debug(
            "Read {} characters from clipboard.".format( len( content ) ) )
        return content
    match cmd.source:
        case '-': return await acquirer.acquire_stdin( )
        case _: return await acquirer.acquire_file( cmd.source )


def _determine_review_mode(
    command: Command, acquirer: ContentAcquirer
) -> _updaters.ReviewModes:
    on_tty = acquirer.stdin_is_tty( )
    if command.mode is None:
        if on_tty: return _updaters.ReviewModes.Partitive
        return _updaters.ReviewModes.Silent
    if not on_tty and command.mode is not _updaters.ReviewModes.Silent:
        _scribe.error( "Cannot use an interactive mode without terminal." )
        raise SystemExit( 1 )
    return command.mode
