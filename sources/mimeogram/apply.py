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

    input: __.typx.Annotated[ # TODO: Rename to 'source'.
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
    base_path: __.typx.Annotated[ # TODO: Rename to 'base'.
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--base-directory', ),
            help = (
                "Base directory for relative locations."
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
        await apply( self )


async def apply( cmd: Command ) -> int:
    ''' Applies mimeogram. '''
    from .exceptions import Omnierror
    from .parsers import parse
    from .updaters import Updater
    try: content = await _acquire_content_to_parse( cmd )
    except Omnierror as exc:
        _scribe.exception( "Could not acquire mimeogram to apply." )
        raise SystemExit( 1 ) from exc
    if not content:
        _scribe.error( "Cannot apply empty mimeogram." )
        raise SystemExit( 1 )
    try: parts = parse( content )
    except Omnierror as exc:
        _scribe.exception( "Could not parse mimeogram." )
        raise SystemExit( 1 ) from exc
    updater = Updater( interactive = cmd.interactive )
    try: await updater.update( parts, base_path = cmd.base_path )
    except Omnierror as exc:
        _scribe.exception( "Could not apply mimeogram." )
        raise SystemExit( 1 ) from exc
    _scribe.info( "Successfully applied mimeogram" )
    raise SystemExit( 0 )


async def _acquire_content_to_parse(
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
    match cmd.input:
        case '-': return __.sys.stdin.read( )
        case _:
            async with __.aiofiles.open( cmd.input, 'r' ) as f:
                return await f.read( )
