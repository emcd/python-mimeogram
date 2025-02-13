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
from . import interfaces as _interfaces
from . import parts as _parts


async def _display_content( target: _parts.Target, content: str ) -> None:
    ''' Displays content in system pager. '''
    from .display import display_content
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( target.part.location ).suffix or '.txt'
    display_content( content, suffix = suffix )


async def _display_differences(
    target: _parts.Target, revision: str
) -> None:
    ''' Displays differences between content and target file. '''
    original = ''
    destination = target.destination
    part = target.part
    if destination.exists( ):
        from .exceptions import ContentAcquireFailure
        try:
            original = (
                await __.acquire_text_file_async(
                    destination, charset = part.charset ) )
        except Exception as exc:
            raise ContentAcquireFailure( destination ) from exc
        original = part.linesep.normalize( original )
    diff = _calculate_differences( part, revision, original )
    if not diff:
        print( "No changes" )
        return
    from .display import display_content as display
    display( '\n'.join( diff ), suffix = '.diff' )


async def _edit_content( target: _parts.Target, content: str ) -> str:
    ''' Edits content in system editor. '''
    from .edit import edit_content
    # Suffix from location for proper syntax highlighting.
    suffix = __.Path( target.destination ).suffix or '.txt'
    return edit_content( content, suffix = suffix )


def _prompt_action(
    target: _parts.Target, content: str, protect: bool
) -> str:
    from readchar import readkey
    from .exceptions import UserOperateCancellation
    menu = _produce_actions_menu( target.part, content, protect )
    print( f"\n{menu} > ", end = '' )
    __.sys.stdout.flush( )
    try: choice = readkey( ).lower( )
    except ( EOFError, KeyboardInterrupt ) as exc:
        print( ) # Add newline to avoid output mangling.
        raise UserOperateCancellation( exc ) from exc
    print( choice ) # Echo.
    return choice


async def _select_segments( target: _parts.Target, content: str ) -> str:
    from .differences import select_segments
    return await select_segments( target, content )


def _validate_choice(
    target: _parts.Target, choice: str # pylint: disable=unused-argument
) -> None:
    if choice.isprintable( ):
        print( f"Invalid choice: {choice}" )
    else: print( "Invalid choice." )


class GenericInteractor(
    _interfaces.PartInteractor,
    decorators = ( __.standard_dataclass, ),
):
    ''' Default console-based interaction handler. '''

    prompter: __.cabc.Callable[
        [ _parts.Target, str, bool ], str ] = _prompt_action
    cdisplayer: __.cabc.Callable[
        [ _parts.Target, str ],
        __.cabc.Coroutine[ None, None, None ] ] = _display_content
    ddisplayer: __.cabc.Callable[
        [ _parts.Target, str ],
        __.cabc.Coroutine[ None, None, None ] ] = _display_differences
    editor: __.cabc.Callable[
        [ _parts.Target, str ],
        __.cabc.Coroutine[ None, None, str ] ] = _edit_content
    sselector: __.cabc.Callable[
        [ _parts.Target, str ],
        __.cabc.Coroutine[ None, None, str ] ] = _select_segments
    validator: __.cabc.Callable[
        [ _parts.Target, str ], None ] = _validate_choice

    async def __call__(
        self, target: _parts.Target
    ) -> tuple[ _parts.Resolutions, str ]:
        # TODO? Track revision history.
        # TODO: Use copies of target object with updated content.
        content = target.part.content
        protect = target.protection.active
        while True:
            # pylint: disable=too-many-function-args
            choice = self.prompter( target, content, protect )
            match choice:
                case 'a' if not protect:
                    return _parts.Resolutions.Apply, content
                case 'd': await self.ddisplayer( target, content )
                case 'e' if not protect:
                    content = await self.editor( target, content )
                case 'i': return _parts.Resolutions.Ignore, content
                case 'p' if protect: protect = False
                case 's' if not protect:
                    content = await self.sselector( target, content )
                case 'v': await self.cdisplayer( target, content )
                case _: self.validator( target, choice )
            # pylint: enable=too-many-function-args


async def interact(
    target: _parts.Target,
    interactor: __.Absential[ _interfaces.PartInteractor ] = __.absent,
) -> tuple[ _parts.Resolutions, str ]:
    ''' Performs interaction for part. '''
    if __.is_absent( interactor ): interactor = GenericInteractor( )
    return await interactor( target )


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
