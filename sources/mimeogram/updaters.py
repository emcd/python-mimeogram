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
from . import fsprotect as _fsprotect
from . import interactions as _interactions
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


class ReviewModes( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Controls how updates are reviewed and applied. '''

    Silent =    'silent'        # Apply parts without review.
    # Aggregate = 'aggregate'     # Git-style aggregated diff for all parts
    Partitive = 'partitive'     # Interactively review each part.


# pylint: disable=bad-reversed-sequence,unsubscriptable-object
# pylint: disable=unsupported-assignment-operation,unsupported-membership-test
class Reverter(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Backup and restore filesystem state. '''

    originals: dict[ __.Path, str ] = (
        __.dataclass_declare( default_factory = dict ) )
    revisions: list[ __.Path ] = (
        __.dataclass_declare( default_factory = list ) )

    async def save( self, part: _parts.Part, path: __.Path ) -> None:
        ''' Saves original file content if it exists. '''
        from .exceptions import ContentAcquireFailure
        if not path.exists( ): return
        try:
            content = (
                await __.acquire_text_file_async(
                    path, charset = part.charset ) )
        except Exception as exc: raise ContentAcquireFailure( path ) from exc
        self.originals[ path ] = content

    async def restore( self ) -> None:
        ''' Restores files to original contents in reverse order. '''
        # TODO: async parallel fanout
        from .exceptions import ContentUpdateFailure
        for path in reversed( self.revisions ):
            if path in self.originals:
                try:
                    await _update_content_atomic(
                        path, self.originals[ path ] )
                except ContentUpdateFailure:
                    _scribe.exception( "Failed to restore {path}" )
            else: path.unlink( )
# pylint: enable=bad-reversed-sequence,unsubscriptable-object
# pylint: enable=unsupported-assignment-operation,unsupported-membership-test


# pylint: disable=no-member,not-an-iterable
class Queue(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Manages queued file updates for batch application. '''

    updates: list[ tuple[ _parts.Part, __.Path, str ] ] = (
        __.dataclass_declare( default_factory = list ) )
    reverter: Reverter = (
        __.dataclass_declare( default_factory = Reverter ) )

    def enqueue(
        self, part: _parts.Part, target: __.Path, content: str
    ) -> None:
        ''' Adds a file update to queue. '''
        self.updates.append( ( part, target, content ) )

    async def apply( self ) -> None:
        ''' Applies all queued updates with parallel async fanout. '''
        try:
            await __.gather_async(
                *(  self.reverter.save( part, target )
                    for part, target, _ in self.updates ),
                error_message = "Failed to backup files." )
            await __.gather_async(
                *(  _update_content_atomic(
                        target, content, charset = part.charset )
                    for part, target, content in self.updates ),
                error_message = "Failed to apply updates." )
        except Exception:
            await self.reverter.restore( )
            raise
        for _, target, _ in self.updates:
            self.reverter.revisions.append( target )
# pylint: enable=no-member,not-an-iterable


async def update( # pylint: disable=too-many-locals
    auxdata: __.Globals,
    parts: __.cabc.Sequence[ _parts.Part ],
    mode: ReviewModes,
    base: __.Absential[ __.Path ] = __.absent,
) -> None:
    ''' Updates filesystem locations from mimeogram. '''
    if __.is_absent( base ): base = __.Path( )
    protector = _fsprotect.Cache.from_configuration( auxdata = auxdata )
    queue = Queue( )
    for part in parts:
        if part.location.startswith( 'mimeogram://' ): continue
        target = _derive_location( part.location, base = base )
        protection = protector.verify( target )
        action, content = await update_part(
            auxdata, part,
            target = target, mode = mode, protection = protection )
        if _interactions.Actions.Ignore is action: continue
        queue.enqueue( part, target, content )
    await queue.apply( )


async def update_part(
    auxdata: __.Globals,
    part: _parts.Part,
    target: __.Path,
    mode: ReviewModes,
    protection: _fsprotect.Status,
) -> tuple[ _interactions.Actions, str ]:
    ''' Updates filesystem location from mimeogram part. '''
    content = part.content
    if ReviewModes.Partitive is mode:
        return await _interactions.prompt_action( part, target, protection )
    options = auxdata.configuration.get( 'update-parts', { } )
    if protection and not options.get( 'disable-protections', False ):
        _scribe.warning(
            f"Skipping protected path: {target} "
            f"Reason: {protection.description}" )
        return _interactions.Actions.Ignore, content
    return _interactions.Actions.Apply, content


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
    import os.path as ospath
    from urllib.parse import urlparse
    from .exceptions import LocationInvalidity
    try: url = urlparse( location )
    except Exception as exc: raise LocationInvalidity( location ) from exc
    match url.scheme:
        case '' | 'file': pass
        case _: raise LocationInvalidity( location )
    location_ = __.Path( ospath.expanduser( ospath.expandvars( url.path ) ) )
    if location_.is_absolute( ): return location_
    if not __.is_absent( base ): return ( base / location_ ).resolve( )
    return __.Path( ) / location_


async def _update_content_atomic(
    location: __.Path,
    content: str,
    charset: str = 'utf-8',
    linesep: _parts.LineSeparators = _parts.LineSeparators.LF
) -> None:
    ''' Updates file content atomically, if possible. '''
    import aiofiles.os as os # pylint: disable=consider-using-from-import
    from aiofiles.tempfile import NamedTemporaryFile
    location.parent.mkdir( parents = True, exist_ok = True )
    content = linesep.nativize( content )
    async with NamedTemporaryFile(
        delete = False,
        dir = location.parent,
        suffix = f"{location.suffix}.tmp",
    ) as stream:
        filename = str( stream.name )
        try:
            await stream.write( content.encode( charset ) )
            await os.replace( filename, str( location ) )
        except Exception as exc:
            from .exceptions import ContentUpdateFailure
            raise ContentUpdateFailure( location ) from exc
        finally:
            if await os.path.exists( filename ):
                await os.remove( filename )
