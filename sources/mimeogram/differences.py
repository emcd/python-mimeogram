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


''' Content differences management. '''


from __future__ import annotations

from . import __
from . import interfaces as _interfaces
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


class ConsoleDisplay(
    _interfaces.DifferencesDisplay, decorators = ( __.standard_dataclass, )
):
    ''' Default display of differences to console. '''

    async def __call__( self, lines: __.cabc.Sequence[ str ] ) -> None:
        from .display import display_content
        if self.inline_threshold >= len( lines ):
            for line in lines: print( line )
            return
        diff = '\n'.join( lines )
        display_content( diff, suffix = '.diff' )


class ConsoleInteractor( _interfaces.DifferencesInteractor ):
    ''' Default console-based interaction handler. '''

    async def __call__(
        self,
        lines: __.cabc.Sequence[ str ],
        display: _interfaces.DifferencesDisplay
    ) -> bool:
        # TODO: Display hunk number.
        from readchar import readkey
        await display( lines )
        menu = "Apply this change? (y)es, (n)o, (v)iew"
        while True:
            print( f"\n{menu} > ", end = '' )
            try: choice = readkey( ).lower( )
            except ( EOFError, KeyboardInterrupt ):
                print( ) # Add newline to avoid output mangling
                return False
            print( choice ) # Echo.
            match choice:
                case 'y': return True
                case 'n': return False
                case 'v': await display( lines )
                case _:
                    if choice.isprintable( ):
                        print( f"Invalid choice: {choice}" )
                    else: print( "Invalid choice." )


async def select_segments(
    target: _parts.Target, revision: str,
    display: __.Absential[ _interfaces.DifferencesDisplay ] = __.absent,
    interactor: __.Absential[ _interfaces.DifferencesInteractor ] = __.absent,
) -> str:
    ''' Selects which diff hunks to apply. '''
    # TODO: Use global state for instance configuration.
    if __.is_absent( display ): display = ConsoleDisplay( )
    if __.is_absent( interactor ): interactor = ConsoleInteractor( )
    # TODO: Acquire destination content from cache.
    part = target.part
    original = (
        await __.acquire_text_file_async(
            target.destination, charset = part.charset ) )
    original = part.linesep.normalize( original )
    if original == revision:
        print( "No changes" )
        return revision
    try:
        revision_ = (
            await _select_segments(
                original, revision,
                display = display, interactor = interactor ) )
    except Exception: # pylint: disable=broad-exception-caught
        _scribe.exception( "Could not process changes" )
        return revision
    return revision_


def _format_segment( # pylint: disable=too-many-arguments,too-many-locals
    current_lines: list[ str ],
    revision_lines: list[ str ],
    i1: int, i2: int,
    j1: int, j2: int,
    context_lines: int = 3,
) -> list[ str ]:
    ''' Formats change block with context lines. '''
    # Calculate context ranges with bounds checking
    start = max( 0, i1 - context_lines )
    end = min( len( current_lines ), i2 + context_lines )
    # Build diff display
    # TODO? Convert non-printables into printable sequences.
    diff: list[ str ] = [ ]
    diff.append(
        f"@@ -{i1 + 1},{i2 - i1} +{j1 + 1},{j2 - j1} @@" )
    for idx in range( start, i1 ):
        diff.append( f" {current_lines[ idx ]}" )
    for idx in range( i1, i2 ):
        diff.append( f"-{current_lines[ idx ]}" )
    for idx in range( j1, j2 ):
        diff.append( f"+{revision_lines[ idx ]}" )
    for idx in range( i2, end ):
        diff.append( f" {current_lines[ idx ]}" )
    return diff


async def _select_segments( # pylint: disable=too-many-locals
    current: str,
    revision: str,
    display: _interfaces.DifferencesDisplay,
    interactor: _interfaces.DifferencesInteractor,
) -> str:
    from patiencediff import PatienceSequenceMatcher # pyright: ignore
    current_lines = current.split( '\n' )
    revision_lines = revision.split( '\n' )
    matcher = PatienceSequenceMatcher( # pyright: ignore
        None, current_lines, revision_lines )
    result: list[ str ] = [ ]
    for op, i1, i2, j1, j2 in matcher.get_opcodes( ):
        if op == 'equal': # pylint: disable=magic-value-comparison
            result.extend( current_lines[ i1:i2 ] )
            continue
        diff_lines = _format_segment(
            current_lines, revision_lines,
            i1, i2, j1, j2,
            context_lines = display.context_lines )
        if not await interactor( diff_lines, display ):
            result.extend( current_lines[ i1:i2 ] )
            continue
        result.extend( revision_lines[ j1:j2 ] )
    return '\n'.join( result )
