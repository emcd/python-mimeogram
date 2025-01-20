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


from __future__ import annotations

import argparse as _argparse

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


@__.dataclass
class Command:
    ''' CLI arguments. '''
    sources: list[ str ]
    recursive: bool = False
    strict: bool = False
    clip: bool = False
    editor_message: bool = False


def add_cli_subparser(
    subparsers: _argparse._SubParsersAction[ __.typx.Any ]
) -> None:
    ''' Adds subparser for command. '''
    parser = subparsers.add_parser(
        'create',
        help = "Creates mimeogram from files/URLs" )
    parser.add_argument(
        'sources',
        nargs = '*',
        help = (
            "File paths or URLs. "
            "If none provided, requires --editor-message." ) )
    parser.add_argument(
        '-r',
        '--recursive',
        action = 'store_true',
        help = "Recurse into directories"
    )
    parser.add_argument(
        '-s',
        '--strict',
        action = 'store_true',
        help = "Fail on first non-textual content instead of skipping" )
    parser.add_argument(
        '--clip',
        action = 'store_true',
        help = "Copy mimeogram to clipboard" )
    parser.add_argument(
        '--editor-message',
        action = 'store_true',
        help = "Spawn editor to capture an initial message part" )


async def create( cmd: Command ) -> int:
    ''' Creates mimeogram. '''
    from .acquirers import acquire
    from .exceptions import Omnierror
    from .formatters import format_bundle
    if cmd.editor_message:
        from .edit import acquire_message
        try: message = acquire_message( )
        except Omnierror as exc:
            _scribe.exception( "Could not acquire user message." )
            raise SystemExit( 1 ) from exc
    else: message = None
    try:
        # TODO: Handle cmd.strict.
        parts = await acquire( cmd.sources, recursive = cmd.recursive )
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
