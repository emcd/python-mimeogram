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


from __future__ import annotations

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


class Command(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Applies mimeogram to filesystem locations. '''

    source: __.typx.Annotated[
        str, # TODO: str | Path
        __.tyro.conf.arg( # pyright: ignore
            help = (
                "Source file for mimeogram. "
                "Defaults to stdin if '--clip' not specified." ) ),
    ] = '-'
    clip: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--clipboard', '--from-clipboard' ),
            help = "Read mimeogram from clipboard instead of file or stdin." ),
    ] = False
    interactive: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            help = "Prompt for action on each part." ),
    ] = False
    base: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--base-directory', ),
            help = (
                "Base directory for relative locations. "
                "Defaults to current working directory." ) ),
    ] = None
    dry_run: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            help = "Show what would be changed without making changes." ),
    ] = False
    force: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            help = 'Override protected path checks' ),
    ] = False

    async def __call__( self, auxdata: __.Globals ) -> None:
        await apply( auxdata, self )


async def apply( auxdata: __.Globals, cmd: Command ) -> int:
    ''' Applies mimeogram. '''
    # TODO? Use BSD sysexits.
    _assert_sanity( cmd )
    from .parsers import parse
    from .updaters import update
    try: mgtext = await _acquire( cmd )
    except Exception as exc:
        _scribe.exception( "Could not acquire mimeogram to apply." )
        raise SystemExit( 1 ) from exc
    if not mgtext:
        _scribe.error( "Cannot apply empty mimeogram." )
        raise SystemExit( 1 )
    try: parts = parse( mgtext )
    except Exception as exc:
        _scribe.exception( "Could not parse mimeogram." )
        raise SystemExit( 1 ) from exc
    # TODO: Pass options DTO.
    nomargs: dict[ str, __.typx.Any ] = dict(
        force = cmd.force, interactive = cmd.interactive )
    if cmd.base: nomargs[ 'base' ] = cmd.base
    try: await update( auxdata, parts, **nomargs )
    except Exception as exc:
        _scribe.exception( "Could not apply mimeogram." )
        raise SystemExit( 1 ) from exc
    _scribe.info( "Successfully applied mimeogram" )
    raise SystemExit( 0 )


async def _acquire(
    cmd: Command
) -> __.typx.Optional[ str ]:
    ''' Acquires content to parse from clipboard, file, or stdin. '''
    if cmd.clip:
        content = _pyperclip.paste( )
        if not content:
            # TODO: Raise exception.
            _scribe.error( "Clipboard is empty" )
            return
        _scribe.debug(
            "Read {} characters from clipboard.".format( len( content ) ) )
        return content
    match cmd.source:
        case '-': return __.sys.stdin.read( )
        case _:
            async with __.aiofiles.open( cmd.source, 'r' ) as f:
                return await f.read( )


def _assert_sanity( command: Command ):
    if not __.sys.stdin.isatty( ) and command.interactive:
        _scribe.error( "Cannot use interactive mode without terminal." )
        raise SystemExit( 1 )
