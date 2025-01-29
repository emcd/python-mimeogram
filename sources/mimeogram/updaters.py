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


''' File content updates. '''


from __future__ import annotations

from . import __
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


class Reverter:
    ''' Backup and restore filesystem state. '''

    def __init__( self ):
        self.originals: dict[ __.Path, str ] = { }
        self.updated: list[ __.Path ] = [ ]

    async def save( self, path: __.Path ) -> None:
        ''' Saves original file content if it exists. '''
        from .exceptions import ContentAcquireFailure
        if not path.exists( ): return
        try:
            # TODO: Do not assume UTF-8 charset.
            async with __.aiofiles.open( path, 'r', encoding = 'utf-8' ) as f:
                self.originals[ path ] = await f.read()
        except Exception as exc: raise ContentAcquireFailure( path ) from exc

    async def restore( self ) -> None:
        ''' Restores files to original contents in reverse order. '''
        # TODO: async parallel fanout
        from .exceptions import ContentUpdateFailure
        for path in reversed( self.updated ):
            if path in self.originals:
                try:
                    await _update_content_atomic(
                        path, self.originals[ path ] )
                except ContentUpdateFailure:
                    _scribe.exception( "Failed to restore {path}" )
            else: path.unlink( )


async def update(
    parts: __.cabc.Sequence[ _parts.Part ],
    # TODO: Use command object as DTO.
    base: __.Absential[ __.Path ] = __.absent,
    interactive: bool = False,
    # TODO: collect/queue
    reverter: __.Absential[ Reverter ] = __.absent,
) -> None:
    ''' Updates filesystem locations from mimeogram. '''
    if __.is_absent( base ): base = __.Path( )
    if __.is_absent( reverter ): reverter = Reverter( )
    for part in parts:
        if part.location.startswith( 'mimeogram://' ): continue
        try:
            await update_part( # TODO: Collect actions for queue.
                part,
                target = _derive_location( part.location, base = base ),
                interactive = interactive,
                reverter = reverter )
        except Exception:
            await reverter.restore( )
            raise


async def update_part(
    part: _parts.Part,
    target: __.Path,
    interactive: bool,
    reverter: Reverter,
) -> None:
    ''' Updates filesystem location from mimeogram part. '''
    content = part.content
    if interactive:
        from .interactions import Action, prompt_action
        action, content_ = await prompt_action( part, target )
        if action == Action.IGNORE: return
        if content_: content = content_
    target.parent.mkdir( parents = True, exist_ok = True )
    await reverter.save( target ) # TODO: Pass part metadata.
    await _update_content_atomic( target, content, charset = part.charset )
    reverter.updated.append( target )


def _derive_location(
    location: __.typx.Annotated[
        str, __.typx.Doc( "Part location (URL or filesystem path)." ) ],
    base: __.typx.Annotated[
        __.Absential[ __.Path ],
        __.typx.Doc(
            "Base path for relative locations. "
            "Defaults to current directory." )
    ] = __.absent,
) -> __.Path:
    ''' Resolves part location to filesystem path. '''
    from urllib.parse import urlparse
    from .exceptions import LocationInvalidity
    try: url = urlparse( location )
    except Exception as exc: raise LocationInvalidity( location ) from exc
    match url.scheme:
        case '' | 'file': pass
        case _: raise LocationInvalidity( location )
    location_ = __.Path( url.path )
    if location_.is_absolute( ): return location_
    if not __.is_absent( base ): return base / location_
    return location_


async def _update_content_atomic(
    location: __.Path,
    content: str,
    charset: str = 'utf-8',
    linesep: _parts.LineSeparators = _parts.LineSeparators.LF
) -> None:
    ''' Updates file content atomically, if possible. '''
    # TODO: Develop safer way to produce temp file on same filesystem.
    #       Probably tempfile with 'dir' argument.
    from .exceptions import ContentUpdateFailure
    tmp = location.with_suffix( f"{location.suffix}.tmp" )
    content = linesep.nativize( content )
    content_bytes = content.encode( charset )
    try: # pylint: disable=too-many-try-statements
        async with __.aiofiles.open( tmp, 'wb' ) as stream:
            await stream.write( content_bytes )
        __.os.replace( str( tmp ), str( location ) )
    except Exception as exc: raise ContentUpdateFailure( location ) from exc
    finally:
        if tmp.exists( ): tmp.unlink( )
