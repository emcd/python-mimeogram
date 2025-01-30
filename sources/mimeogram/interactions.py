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


''' User interactions and automations. '''


from __future__ import annotations

from . import __
from . import fsprotect as _fsprotect
from . import parts as _parts


class Action( __.enum.Enum ):
    ''' Available actions for each part in interactive mode. '''
    APPLY =     'apply'     # Write to filesystem
    DIFF =      'diff'      # Show changes
    EDIT =      'edit'      # Edit in $EDITOR
    IGNORE =    'ignore'    # Skip
    VIEW =      'view'      # Display in $PAGER


async def display_content( part: _parts.Part ) -> None:
    ''' Displays part content in system pager. '''
    from .display import display_content as display
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( part.location ).suffix or '.txt'
    display( part.content, suffix = suffix )


async def display_differences(
    part: _parts.Part,
    target: __.Path
) -> None:
    ''' Displays differences between part content and target file. '''
    current_content = None
    if target.exists( ):
        current_content = await _acquire_content( target, part.charset )
    diff_lines = _calculate_differences(
        part.content, current_content, target )
    if not diff_lines:
        print( "No changes" )
        return
    from .display import display_content as display
    display( '\n'.join( diff_lines ), suffix = '.diff' )


async def edit_content( part: _parts.Part ) -> __.typx.Optional[ str ]:
    ''' Edits part content in system editor. '''
    from .edit import edit_content as edit
    from .exceptions import EditorFailure
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( part.location ).suffix or '.txt'
    try: edited = edit( part.content, suffix = suffix )
    except Exception as exc: raise EditorFailure( exc ) from exc
    if edited != part.content: return edited
    return


async def prompt_action(
    part: _parts.Part, target: __.Path, protection: _fsprotect.Status
) -> tuple[ Action, str ]:
    ''' Prompts user for action on current part. '''
    # TODO: Support queuing of applies for parallel async update.
    from .exceptions import UserOperateCancellation
    if not __.sys.stdin.isatty( ):
        # Default to APPLY if we cannot prompt.
        # TODO: Error or default action?
        return Action.APPLY, part.content
    content = part.content
    protect = protection.active
    while True:
        menu = _produce_actions_menu( part, content, protect )
        print( menu, end = '' )
        try: choice = input( " > " ).strip( ).lower( )
        except ( EOFError, KeyboardInterrupt ) as exc:
            print( ) # Add newline to avoid output mangling.
            raise UserOperateCancellation( exc ) from exc
        match choice:
            case 'a' | 'apply': return Action.APPLY, content
            case 'd' | 'diff': await display_differences( part, target )
            case 'e' | 'edit':
                edited = await edit_content( part )
                if edited is not None: content = edited
            case 'i' | 'ignore': return Action.IGNORE, ''
            case 'p' | 'permit': protect = False
            case 'v' | 'view': await display_content( part )
            case _: print( f"Invalid choice: {choice}" )
        continue


async def _acquire_content( path: __.Path, encoding: str = 'utf-8' ) -> str:
    ''' Acquires content from target file. '''
    # TODO: Merge with logic in acquirers module.
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
        lineterm = '' ) )


def _produce_actions_menu(
    part: _parts.Part, content: str, protect: bool
) -> str:
    info = "{location:<30} [{size}]".format(
        location = part.location, size = len( content ) )
    if protect: return f"{info} : (d)iff, (i)gnore, (p)ermit, (v)iew"
    return f"{info} : (a)pply, (d)iff, (e)dit, (i)gnore, (v)iew"
