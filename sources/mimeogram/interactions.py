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


class Actions( __.enum.Enum ):
    ''' Available actions for each part in interactive mode. '''
    APPLY =     'apply'     # Write to filesystem
    DIFF =      'diff'      # Show changes
    EDIT =      'edit'      # Edit in $EDITOR
    IGNORE =    'ignore'    # Skip
    VIEW =      'view'      # Display in $PAGER


async def display_content( part: _parts.Part, content: str ) -> None:
    ''' Displays content in system pager. '''
    from .display import display_content as display
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( part.location ).suffix or '.txt'
    display( content, suffix = suffix )


async def display_differences(
    part: _parts.Part, target: __.Path, revision: str
) -> None:
    ''' Displays differences between content and target file. '''
    original = ''
    if target.exists( ):
        from .exceptions import ContentAcquireFailure
        try:
            original = (
                await __.acquire_text_file_async(
                    target, charset = part.charset ) )
        except Exception as exc:
            raise ContentAcquireFailure( target ) from exc
        original = part.linesep.normalize( original )
    diff = _calculate_differences( part, revision, original )
    if not diff:
        print( "No changes" )
        return
    from .display import display_content as display
    display( '\n'.join( diff ), suffix = '.diff' )


async def edit_content( target: __.Path, content: str ) -> str:
    ''' Edits content in system editor. '''
    from .edit import edit_content as edit
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( target ).suffix or '.txt'
    return edit( content, suffix = suffix )


async def prompt_action(
    part: _parts.Part, target: __.Path, protection: _fsprotect.Status
) -> tuple[ Actions, str ]:
    ''' Prompts user for action on current part. '''
    # TODO? Track revision history.
    # TODO: Support queuing of applies for parallel async update.
    from .differences import select_segments
    from .exceptions import UserOperateCancellation
    if not __.sys.stdin.isatty( ):
        # Default to APPLY if we cannot prompt.
        # TODO: Error or default action?
        return Actions.APPLY, part.content
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
            case 'a' | 'apply': return Actions.APPLY, content
            case 'd' | 'diff':
                await display_differences( part, target, content )
            case 'e' | 'edit':
                content = await edit_content( target, content )
            case 'i' | 'ignore': return Actions.IGNORE, ''
            case 'p' | 'permit': protect = False
            case 's' | 'select':
                content = await select_segments( part, target, content )
            case 'v' | 'view':
                await display_content( part, content )
            case _: print( f"Invalid choice: {choice}" )
        continue


def _calculate_differences(
    part: _parts.Part,
    revision: str,
    original: __.Absential[ str ] = __.absent,
) -> list[ str ]:
    ''' Generates unified diff between contents. '''
    from patiencediff import (
        unified_diff, PatienceSequenceMatcher ) # pyright: ignore
    from_lines = (
        original.split( '\n' )
        if not __.is_absent( original ) else [ ] )
    to_lines = revision.split( '\n' )
    from_file = (
        part.location
        if not __.is_absent( original ) else '/dev/null' )
    to_file = part.location
    return list( unified_diff( # pyright: ignore
        from_lines, to_lines,
        fromfile = from_file, tofile = to_file,
        lineterm = '', sequencematcher = PatienceSequenceMatcher ) )


def _produce_actions_menu(
    part: _parts.Part, content: str, protect: bool
) -> str:
    info = "{location:<30} [{size}]".format(
        location = part.location, size = len( content ) )
    # TODO: Add warning indicator when target is protected.
    if protect: return f"{info} : (d)iff, (i)gnore, (p)ermit, (v)iew"
    return f"{info} : (a)pply, (d)iff, (e)dit, (i)gnore, (s)elect, (v)iew"
