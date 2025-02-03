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
    ''' Available actions for each part. '''

    Apply =     'apply'     # Write to filesystem
    Ignore =    'ignore'    # Skip


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


async def prompt_action( # pylint: disable=too-many-locals
    part: _parts.Part, target: __.Path, protection: _fsprotect.Status
) -> tuple[ Actions, str ]:
    ''' Prompts user for action on current part. '''
    # TODO? Track revision history.
    # TODO: Support queuing of applies for parallel async update.
    from readchar import readkey
    from .differences import select_segments
    from .exceptions import UserOperateCancellation
    content = part.content
    protect = protection.active
    while True:
        menu = _produce_actions_menu( part, content, protect )
        print( f"\n{menu} > ", end = '' )
        __.sys.stdout.flush( )
        try: choice = readkey( ).lower( )
        except ( EOFError, KeyboardInterrupt ) as exc:
            print( ) # Add newline to avoid output mangling.
            raise UserOperateCancellation( exc ) from exc
        print( choice ) # Echo.
        match choice:
            case 'a' if not protect: return Actions.Apply, content
            case 'd': await display_differences( part, target, content )
            case 'e' if not protect:
                content = await edit_content( target, content )
            case 'i': return Actions.Ignore, content
            case 'p' if protect: protect = False
            case 's' if not protect:
                content = await select_segments( part, target, content )
            case 'v': await display_content( part, content )
            case _:
                if choice.isprintable( ): print( f"Invalid choice: {choice}" )
                else: print( "Invalid choice." )


def _calculate_differences(
    part: _parts.Part,
    revision: str,
    original: __.Absential[ str ] = __.absent,
) -> list[ str ]:
    ''' Generates unified diff between contents. '''
    from patiencediff import (
        unified_diff, PatienceSequenceMatcher ) # pyright: ignore
    from_lines = (
        original.split( '\n' ) if not __.is_absent( original ) else [ ] )
    to_lines = revision.split( '\n' )
    from_file = (
        part.location if not __.is_absent( original ) else '/dev/null' )
    to_file = part.location
    return list( unified_diff( # pyright: ignore
        from_lines, to_lines,
        fromfile = from_file, tofile = to_file,
        lineterm = '', sequencematcher = PatienceSequenceMatcher ) )


def _produce_actions_menu(
    part: _parts.Part, content: str, protect: bool
) -> str:
    size = len( content )
    size_str = (
        "{:.1f}K".format( size / 1024 )
        if 1024 <= size # pylint: disable=magic-value-comparison
        else f"{size}B" )
    status = "[PROTECTED]" if protect else ""
    info = f"{part.location} [{size_str}] {status}"
    if protect:
        return (
            f"{info}\n"
            "Action? (d)iff, (i)gnore, (p)ermit changes, (v)iew" )
    return (
        f"{info}\n"
        "Action? (a)pply, (d)iff, (e)dit, (i)gnore, (s)elect hunks, (v)iew" )
