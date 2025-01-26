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

import pyperclip as _pyperclip

from . import __


_scribe = __.produce_scribe( __name__ )


class Command(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Creates mimeogram from filesystem locations or URLs. '''

    sources: __.typx.Annotated[
        __.tyro.conf.Positional[ list[ str ] ],
        __.tyro.conf.arg( # pyright: ignore
            help = "Filesystem locations or URLs.",
            prefix_name = False ),
    ]
    clip: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '--clipboard', '--to-clipboard' ),
            help = "Copy mimeogram to clipboard." ),
    ] = False
    edit: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '-e', '--edit-message' ),
            help = "Spawn editor to capture an introductory message." ),
    ] = False
    recurse: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            aliases = ( '-r', '--recurse-directories', '--recursive' ),
            help = "Recurse into directories." ),
    ] = False
    strict: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( # pyright: ignore
            help = "Fail on invalid contents instead of skipping them." ),
    ] = False

    async def __call__( self, auxdata: __.Globals ) -> None:
        await create( self )


async def create( cmd: Command ) -> int:
    ''' Creates mimeogram. '''
    from .acquirers import acquire
    from .exceptions import Omnierror
    from .formatters import format_bundle
    if cmd.edit:
        from .edit import acquire_message
        try: message = acquire_message( )
        except Omnierror as exc:
            _scribe.exception( "Could not acquire user message." )
            raise SystemExit( 1 ) from exc
    else: message = None
    try:
        # TODO: Handle cmd.strict.
        parts = await acquire( cmd.sources, recursive = cmd.recurse )
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
