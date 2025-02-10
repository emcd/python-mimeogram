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
    editor = (
            __.os.environ.get( 'VISUAL' )
        or  __.os.environ.get( 'EDITOR' )
        # TODO: Better default for Windows.
        or  'nano' )
    # TODO: Platform-specific list.
    for editor_ in ( editor, 'nano' ):
        if which( editor_ ):
            editor = editor_
            break
    else: editor = ''

    if editor:

        # TODO? async
        def editor_executor( filename: str ) -> str:
            ''' Executes editor with file. '''
            run( ( editor, filename ), check = True ) # nosec B603
            with open( filename, 'r', encoding = 'utf-8' ) as stream:
                return stream.read( )

        return editor_executor

    from .exceptions import ProgramAbsenceError
    raise ProgramAbsenceError( 'editor' )


def edit_content(
    content: str = '', *,
    suffix: str = '.md',
    editor_discoverer: __.cabc.Callable[
        [ ], __.cabc.Callable[ [ str ], str ] ] = discover_editor,
) -> str:
    ''' Edits content via discovered editor. '''
    from .exceptions import EditorFailure, ProgramAbsenceError
    try: editor = editor_discoverer( )
    except ProgramAbsenceError:
        _scribe.exception( "Could not find editor program." )
        return content
    import tempfile
    with tempfile.NamedTemporaryFile( mode = 'r+', suffix = suffix ) as tmp:
        tmp.write( content )
        tmp.flush( )
        try: return editor( tmp.name )
        except Exception as exc: raise EditorFailure( cause = exc ) from exc
