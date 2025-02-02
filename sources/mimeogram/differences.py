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
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


class DisplayOptions(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, )
):
    ''' Configuration for differences display. '''

    context_lines: int = 3
    inline_threshold: int = 24 # TODO: Adjust to terminal height.
    # TODO: colorize: bool = False
    # TODO: emojify: bool = False
    # TODO: show_whitespace: bool = False
    # TODO: truncate_lines: bool = False
    # TODO: wrap_lines: bool = False


async def select_segments(
    part: _parts.Part, target: __.Path, revision: str
) -> str:
    ''' Selects which diff hunks to apply. '''
    # TODO: Pass display options from configuration.
    # TODO: Acquire target content from cache.
    original = (
        await __.acquire_text_file_async(
            target, charset = part.charset ) )
    original = part.linesep.normalize( original )
    if original == revision:
        print( "No changes" )
        return revision
    try: revision_ = _select_segments( original, revision )
    except Exception: # pylint: disable=broad-exception-caught
        _scribe.exception( "Could not process changes" )
        return revision
    return revision_


def _display_differences(
    lines: list[ str ], display_options: DisplayOptions
) -> None:
    from .display import display_content
    if display_options.inline_threshold >= len( lines ):
        for line in lines: print( line )
        return
    diff = '\n'.join( lines )
    display_content( diff, suffix = '.diff' )


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


def _prompt_segment_action(
    lines: list[ str ], display_options: DisplayOptions
) -> bool:
    ''' Displays change and gets user decision. '''
    _display_differences( lines, display_options )
    while True:
        try: choice = input( "Apply this change? (y)es, (n)o, (v)iew > " )
        except ( EOFError, KeyboardInterrupt ):
            print( ) # Add newline to avoid output mangling
            return False
        match choice.strip( ).lower( ):
            case 'y' | 'yes': return True
            case 'n' | 'no': return False
            case 'v' | 'view':
                _display_differences( lines, display_options )
                continue
            case _:
                print( f"Invalid choice: {choice}" )
                continue


def _select_segments( # pylint: disable=too-many-locals
    current: str,
    revision: str,
    display_options: __.Absential[ DisplayOptions ] = __.absent,
) -> str:
    from patiencediff import PatienceSequenceMatcher # pyright: ignore
    from .exceptions import DifferencesProcessFailure
    if __.is_absent( display_options ): display_options = DisplayOptions( )
    current_lines = current.split( '\n' )
    revision_lines = revision.split( '\n' )
    matcher = PatienceSequenceMatcher( # pyright: ignore
        None, current_lines, revision_lines )
    result: list[ str ] = [ ]
    for op, i1, i2, j1, j2 in matcher.get_opcodes( ):
        if op == 'equal': # pylint: disable=magic-value-comparison
            result.extend( current_lines[ i1:i2 ] )
            continue
        try:
            diff_lines = _format_segment(
                current_lines, revision_lines,
                i1, i2, j1, j2,
                context_lines = display_options.context_lines )
        except Exception as exc:
            raise DifferencesProcessFailure( # noqa: TRY003
                "Could not format change block." ) from exc
        if not _prompt_segment_action( diff_lines, display_options ):
            result.extend( current_lines[ i1:i2 ] )
            continue
        result.extend( revision_lines[ j1:j2 ] )
    return '\n'.join( result )
