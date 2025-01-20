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

import argparse as _argparse

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


@__.dataclass
class Command:
    ''' CLI arguments. '''
    input: str
    clip: bool = False
    base_path: __.typx.Optional[ __.Path ] = None
    interactive: bool = False
    # force: bool = False
    dry_run: bool = False


def add_cli_subparser(
    subparsers: _argparse._SubParsersAction[ __.typx.Any ]
) -> None:
    ''' Adds subparser for command. '''
    parser_apply = subparsers.add_parser(
        'apply',
        help = "Applies mimeogram to filesystem locations" )
    parser_apply.add_argument(
        'input',
        nargs = '?',
        default = '-',
        help = "Input file (default: stdin if --clip not specified)" )
    parser_apply.add_argument(
        '--clip',
        action = 'store_true',
        help = "Read mimeogram from clipboard instead of file/stdin" )
    parser_apply.add_argument(
        '--base-path',
        type = __.Path,
        help = "Base path for relative locations" )
    parser_apply.add_argument(
        '--interactive',
        action = 'store_true',
        help = "Prompt for action on each part" )
    # parser_apply.add_argument(
    #     '--force',
    #     action = 'store_true',
    #     help = 'Override protected path checks' )
    parser_apply.add_argument(
        '--dry-run',
        action = 'store_true',
        help = "Show what would be changed without making changes" )


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
