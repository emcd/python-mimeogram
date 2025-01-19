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
from . import parser as _parser


_scribe = __.produce_scribe( __name__ )


class Reverter:
    ''' Backup and restore filesystem state. '''

    def __init__( self ):
        self.originals: dict[ __.Path, str ] = {}
        self.updated: list[ __.Path ] = []

    async def save( self, path: __.Path ) -> None:
        ''' Saves original file content if it exists. '''
        from .exceptions import ContentAcquireFailure
        if not path.exists( ): return
        try:
            async with __.aiofiles.open( path, 'r', encoding = 'utf-8' ) as f:
                self.originals[ path ] = await f.read()
        except Exception as exc: raise ContentAcquireFailure( path ) from exc

    async def restore( self ) -> None:
        ''' Restores files to original contents in reverse order. '''
        from .exceptions import Omnierror
        for path in reversed( self.updated ):
            if path in self.originals:
                try:
                    await _update_content_atomic(
                        path, self.originals[ path ] )
                except Omnierror:
                    _scribe.exception( 'Failed to restore %s', path )
            else: path.unlink( )


class Updater:
    ''' Updates filesystem with mimeogram part contents. '''

    def __init__(
        self,
        *,
        interactive: bool = True,
        reverter: __.typx.Optional[ Reverter ] = None,
    ):
        self.interactive = interactive
        self.reverter = reverter or Reverter()

    def _get_path(
        self,
        location: __.typx.Annotated[
            str, __.typx.Doc( "Part location (URL or path)" ) ],
        base_path: __.typx.Annotated[
            __.typx.Optional[ __.Path ],
            __.typx.Doc( "Base path for relative locations" )
        ] = None,
    ) -> __.Path:
        ''' Resolves part location to filesystem path. '''
        from .exceptions import LocationInvalidity
        if location.startswith( 'mimeogram://' ):
            raise LocationInvalidity( location )
        path = __.Path( location )
        if not path.is_absolute( ) and base_path is not None:
            path = base_path / path
        return path

    async def _process_part(
        self,
        part: _parser.Part,
        base_path: __.typx.Optional[ __.Path ]
    ) -> __.typx.Optional[ __.Path ]:
        ''' Updates file from part content. '''
        # TODO: Work with various kinds of interactors.
        from .exceptions import ContentUpdateFailure
        if part.location.startswith( 'mimeogram://' ): return
        target = self._get_path( part.location, base_path )
        if self.interactive:
            from .interactions import Action, prompt_action
            action, content = await prompt_action( part, target )
            if action == Action.IGNORE: return
            if content: part.content = content
        target.parent.mkdir( parents = True, exist_ok = True )
        await self.reverter.save( target )
        try:
            await _update_content_atomic(
                target, part.content, encoding = part.charset )
        except ContentUpdateFailure:
            await self.reverter.restore( )
            raise
        self.reverter.updated.append( target )
        return target

    async def update(
        self,
        parts: __.cabc.Sequence[ _parser.Part ],
        base_path: __.typx.Optional[ __.Path ] = None,
    ) -> None:
        ''' Update filesystem with content from parts. '''
        try:
            for part in parts:
                await self._process_part( part, base_path )
        except Exception:
            await self.reverter.restore( )
            raise


async def _update_content_atomic(
    path: __.Path,
    content: str,
    encoding: str = 'utf-8'
) -> None:
    ''' Updates file content atomically. '''
    # TODO: Develop safer way to produce temp file on same filesystem.
    from .exceptions import ContentUpdateFailure
    temp_path = path.with_suffix( f"{path.suffix}.tmp" )
    try:
        async with __.aiofiles.open(
            temp_path, 'w', encoding = encoding
        ) as f: await f.write( content )
        __.os.replace( str( temp_path ), str( path ) )
    except Exception as exc: raise ContentUpdateFailure( path ) from exc
    finally:
        if temp_path.exists( ): temp_path.unlink( )
