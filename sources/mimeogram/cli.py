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


''' Command-line interface for mimeogram. '''


from __future__ import annotations

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


@__.dataclass
class CreateCommand:
    ''' Parameters for create command. '''
    sources: list[ str ]
    recursive: bool = False
    strict: bool = False
    clip: bool = False
    editor_message: bool = False


@__.dataclass
class ApplyCommand:
    ''' Parameters for apply command. '''
    input: str
    clip: bool = False
    base_path: __.typx.Optional[ __.Path ] = None
    interactive: bool = False
    # force: bool = False
    dry_run: bool = False


async def create( cmd: CreateCommand ) -> int:
    ''' Creates mimeogram. '''
    from .acquirers import Acquirer
    from .exceptions import Omnierror
    from .format import format_bundle
    if cmd.editor_message:
        from .editor import acquire_message
        try: message = acquire_message( )
        except Omnierror as exc:
            _scribe.exception( "Could not acquire user message." )
            raise SystemExit( 1 ) from exc
    else: message = None
    try:
        async with Acquirer( strict = cmd.strict ) as acquirer:
            parts = await acquirer.acquire(
                cmd.sources, recursive = cmd.recursive )
    except Omnierror as exc:
        _scribe.exception( "Could not acquire mimeogram parts." )
        raise SystemExit( 1 ) from exc
    mimeogram = format_bundle( parts, message = message )
    if cmd.clip:
        try: _pyperclip.copy( mimeogram )
        except Exception as exc:
            _scribe.exception( "Could not copy mimeogram to clipboard." )
            raise SystemExit( 1 ) from exc
        _scribe.info( "Copied mimeogram to clipboard." )
    else: print( mimeogram )
    raise SystemExit( 0 )


async def apply( cmd: ApplyCommand ) -> int:
    ''' Applies mimeogram. '''
    from .exceptions import Omnierror
    from .parser import parse
    from .updater import Updater
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


def create_parser( ) -> __.typx.Any:
    ''' Creates argument parser. '''
    import argparse
    parser = argparse.ArgumentParser(
        description = "Creates and applies mimeograms." )
    parser.add_argument(
        '-v',
        '--verbose',
        action = 'store_true',
        help = "Enables verbose logging" )
    subparsers = parser.add_subparsers(
        title = 'commands',
        dest = 'command',
        required = True )

    parser_create = subparsers.add_parser(
        'create',
        help = "Creates mimeogram from files/URLs" )
    parser_create.add_argument(
        'sources',
        nargs = '*',
        help = (
            "File paths or URLs. "
            "If none provided, requires --editor-message." ) )
    parser_create.add_argument(
        '-r',
        '--recursive',
        action = 'store_true',
        help = "Recurse into directories"
    )
    parser_create.add_argument(
        '-s',
        '--strict',
        action = 'store_true',
        help = "Fail on first non-textual content instead of skipping" )
    parser_create.add_argument(
        '--clip',
        action = 'store_true',
        help = "Copy mimeogram to clipboard" )
    parser_create.add_argument(
        '--editor-message',
        action = 'store_true',
        help = "Spawn editor to capture an initial message part" )

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

    return parser


async def main( args: __.typx.Optional[ __.cabc.Sequence[ str ] ] = None ):
    ''' CLI entry point. '''
    parser = create_parser( )
    parsed_args = parser.parse_args( args )
    _setup_logging( parsed_args.verbose )
    match parsed_args.command:
        case 'create':
            await create( CreateCommand(
                sources = parsed_args.sources,
                recursive = parsed_args.recursive,
                strict = parsed_args.strict,
                clip = parsed_args.clip,
                editor_message = parsed_args.editor_message
            ) )
        case 'apply':
            await apply( ApplyCommand(
                input = parsed_args.input,
                clip = parsed_args.clip,
                base_path = parsed_args.base_path,
                interactive = parsed_args.interactive,
                # force = parsed_args.force,
                dry_run = parsed_args.dry_run
            ) )
        case _:
            parser.print_help( )
            raise SystemExit( 1 )


async def _acquire_content_to_parse(
    cmd: ApplyCommand
) -> __.typx.Optional[ str ]:
    ''' Acquires content to parse from clipboard, file, or stdin. '''
    if cmd.clip:
        content = _pyperclip.paste( )
        if not content:
            # TODO: Raise exception.
            _scribe.error( "Clipboard is empty" )
            return None
        _scribe.debug(
            "Read {} characters from clipboard.".format( len( content ) ) )
        return content
    match cmd.input:
        case '-': return __.sys.stdin.read( )
        case _:
            async with __.aiofiles.open( cmd.input, 'r' ) as f:
                return await f.read( )


def _setup_logging( verbose: bool ) -> None:
    ''' Configures logging based on verbosity. '''
    import logging
    if verbose:
        logging.basicConfig(
            level = logging.DEBUG,
            format = "%(levelname)s:%(name)s:%(message)s" )
    else:
        logging.basicConfig(
            level = logging.INFO,
            format = "%(levelname)s:%(message)s" )


if __name__ == '__main__': __.asyncio.run( main( ) )
