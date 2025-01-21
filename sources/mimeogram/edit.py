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


def acquire_message( initial_text: str = '', *, suffix: str = '.md' ) -> str:
    ''' Acquires message via system editor. '''
    import subprocess # nosec B404
    import tempfile
    from .exceptions import EditorFailure
    # TODO: Refactor into editor finder.
    editor = (
            __.os.environ.get( 'VISUAL' )
        or  __.os.environ.get( 'EDITOR' )
        # TODO: Better default for Windows.
        or  'nano' )
    with tempfile.NamedTemporaryFile( mode = 'r+', suffix = suffix ) as tmp:
        tmp_path = tmp.name
        tmp.write( initial_text )
        tmp.flush( )
        # TODO: Refactor into helper functions.
        try:
            result = subprocess.run( # nosec B603
                [ editor, tmp_path ], check=True )
        except subprocess.SubprocessError as exc:
            raise EditorFailure( cause = exc ) from exc
        if result.returncode != 0:
            raise EditorFailure(
                cause = f"Exited with status {result.returncode}" )
        try: tmp.seek( 0 )
        except Exception as exc: raise EditorFailure( cause = exc ) from exc
        try: return tmp.read( )
        except Exception as exc: raise EditorFailure( cause = exc ) from exc
