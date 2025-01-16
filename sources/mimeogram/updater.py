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
from .parser import ParsedPart as _ParsedPart


_scribe = __.produce_scribe( __name__ )


class Action( __.enum.Enum ):
    ''' Available actions for each part in interactive mode. '''
    APPLY =     'apply'     # Write to filesystem
    DIFF =      'diff'      # Show changes
    EDIT =      'edit'      # Edit in $EDITOR
    IGNORE =    'ignore'    # Skip
    VIEW =      'view'      # Display in $PAGER


async def display_differences(
    part: _ParsedPart,
    target: __.Path
) -> None:
    ''' Displays differences between current content and target file. '''
    current_content = None
    if target.exists():
        current_content = await _acquire_content( target, part.charset )
    diff_lines = _calculate_differences(
        part.content,
        current_content,
        target )
    if not diff_lines:
        print( "No changes" )
        return
    from .display import Pager
    Pager.display_content( '\n'.join(diff_lines), suffix = '.diff' )


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


class UserInteraction:
    ''' Interacts with user during application of mimeogram parts. '''
    # TODO: Refactor into separate module and break into functions.

    async def edit_content(
        self, part: _ParsedPart
    ) -> __.typx.Optional[ str ]:
        ''' Edits part content in system editor. '''
        from .editor import read_message
        from .exceptions import EditorFailure
        # Suffix from location for proper syntax highlighting.
        suffix = __.Path( part.location ).suffix or '.txt'
        try: edited = read_message( part.content, suffix = suffix )
        except Exception as exc: raise EditorFailure( exc) from exc
        if edited != part.content: return edited
        return None

    async def view_content( self, part: _ParsedPart ) -> None:
        ''' Displays part content in system pager. '''
        # TODO: Convert to function from object.
        from .display import Pager
        # Suffix from location for proper syntax highlighting.
        suffix = __.Path( part.location ).suffix or '.txt'
        Pager.display_content( part.content, suffix = suffix )

    async def prompt_action(
        self, part: _ParsedPart, target: __.Path
    ) -> tuple[ Action, str ]:
        ''' Prompts user for action on current part. '''
        # TODO: Support queuing of applies for parallel async update.
        from .exceptions import UserOperateCancellation
        if not __.sys.stdin.isatty():
            # Default to APPLY if we cannot prompt.
            # TODO: Error or default action?
            return Action.APPLY, part.content
        content = part.content
        while True:
            # TODO: Dynamically generate menu.
            #       Consider whether user edit exists, etc....
            print(
                f"{part.location:<30} [{len(content)} bytes] : "
                "(a)pply, (d)iff, (e)dit, (i)gnore, (v)iew",
                end = '' )
            try: choice = input( " > " ).strip( ).lower( )
            except ( EOFError, KeyboardInterrupt ) as exc:
                print( ) # Add newline to avoid output mangling.
                raise UserOperateCancellation( exc ) from exc
            match choice:
                case 'a' | 'apply': return Action.APPLY, content
                case 'd' | 'diff': await display_differences( part, target )
                case 'e' | 'edit':
                    edited = await self.edit_content( part )
                    if edited is not None:
                        content = edited
                case 'i' | 'ignore': return Action.IGNORE, None
                case 'v' | 'view': await self.view_content( part )
                case _: print( f"Invalid choice: {choice}" )
            continue


class Updater:
    ''' Updates filesystem with mimeogram part contents. '''

    def __init__(
        self,
        *,
        interactive: bool = True,
        reverter: __.typx.Optional[ Reverter ] = None,
        interaction: __.typx.Optional[ UserInteraction ] = None
    ):
        self.interactive = interactive
        self.reverter = reverter or Reverter()
        self.interaction = interaction or UserInteraction()

    def _get_path(
        self,
        location: __.typx.Annotated[
            str, __.typx.Doc( "Part location (URL or path)" ) ],
        base_path: __.typx.Annotated[
            __.typx.Optional[ __.Path ],
            __.typx.Doc( "Base path for relative locations" )
        ] = None
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
        part: _ParsedPart,
        base_path: __.typx.Optional[ __.Path ]
    ) -> __.typx.Optional[ __.Path ]:
        ''' Updates file from part content. '''
        # TODO: Work with various kinds of interactors.
        from .exceptions import ContentUpdateFailure
        if part.location.startswith( 'mimeogram://' ): return None
        target = self._get_path( part.location, base_path )
        if self.interactive:
            action, content = (
                await self.interaction.prompt_action( part, target ) )
            if action == Action.IGNORE: return None
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
        parts: __.cabc.Sequence[_ParsedPart],
        base_path: __.typx.Optional[__.Path] = None,
        *,
        force: bool = False
    ) -> None:
        ''' Update filesystem with content from parts. '''
        try:
            for part in parts:
                await self._process_part( part, base_path )
        except Exception:
            await self.reverter.restore()
            raise


async def _acquire_content( path: __.Path, encoding: str = 'utf-8' ) -> str:
    ''' Acquires content from target file. '''
    from .exceptions import ContentAcquireFailure
    try:
        async with __.aiofiles.open( path, 'r', encoding = encoding ) as f:
            return await f.read()
    except Exception as exc: raise ContentAcquireFailure( path ) from exc


def _calculate_differences(
    new_content: str,
    current_content: __.typx.Optional[ str ],
    target_path: __.Path
) -> list[ str ]:
    ''' Generates unified diff between contents. '''
    import difflib
    from_lines = (
        current_content.splitlines( keepends = True )
        if current_content else [ ] )
    to_lines = new_content.splitlines( keepends = True )
    from_file = str( target_path ) if current_content else '/dev/null'
    to_file = str( target_path )
    return list( difflib.unified_diff(
        from_lines,
        to_lines,
        fromfile = from_file,
        tofile = to_file,
        lineterm = ''
    ) )


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
