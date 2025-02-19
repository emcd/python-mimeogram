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


''' System editor interaction. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


def discover_editor( ) -> __.cabc.Callable[ [ str ], str ]:
    ''' Discovers editor and returns executor function. '''
    from shutil import which
    from subprocess import run # nosec B404
    editor = __.os.environ.get( 'VISUAL' ) or  __.os.environ.get( 'EDITOR' )
    for editor_ in filter(
        None,
        # Editors, ranked by "friendliness", not by personal preference.
        ( editor, 'code', 'nano', 'emacs', 'nvim', 'vim' )
    ):
        if ( editor := which( editor_ ) ): break
    else: editor = ''
    match editor:
        case 'code': posargs = ( '--wait', )
        case _: posargs = ( )

    if editor:

        # TODO? async
        def editor_executor( filename: str ) -> str:
            ''' Executes editor with file. '''
            run( ( editor, *posargs, filename ), check = True ) # nosec B603
            with open( filename, 'r', encoding = 'utf-8' ) as stream:
                return stream.read( )

        return editor_executor

    _scribe.error(
        "No suitable text editor found. "
        "Please install a console-based editor "
        "or set the 'EDITOR' environment variable to your preferred editor." )
    # TODO: Add suggestions.
    from .exceptions import ProgramAbsenceError
    raise ProgramAbsenceError( 'editor' )


def edit_content( # pylint: disable=too-many-locals
    content: str = '', *,
    suffix: str = '.md',
    editor_discoverer: __.cabc.Callable[
        [ ], __.cabc.Callable[ [ str ], str ] ] = discover_editor,
) -> str:
    ''' Edits content via discovered editor. '''
    from .exceptions import EditorFailure, ProgramAbsenceError
    try: editor = editor_discoverer( )
    except ProgramAbsenceError: return content
    import tempfile
    from pathlib import Path
    # Using delete = False to handle file cleanup manually. This ensures
    # the file handle is properly closed before the editor attempts to read it,
    # which is particularly important on Windows where open files cannot be
    # simultaneously accessed by other processes without a read share.
    with tempfile.NamedTemporaryFile(
        mode = 'w', suffix = suffix, delete = False, encoding = 'utf-8'
    ) as tmp:
        filename = tmp.name
        tmp.write( content )
    try: return editor( filename ) # noqa: TRY101
    except Exception as exc: raise EditorFailure( cause = exc ) from exc
    finally:
        try: Path( filename ).unlink( )
        except Exception: # pylint: disable=broad-exception-caught
            _scribe.exception( f"Failed to cleanup {filename}" )
