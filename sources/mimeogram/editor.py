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


_scribe = __.produce_scribe(__name__)


def read_message(initial_text: str = '', *, suffix: str = '.md') -> str:
    """Spawn system editor to capture message."""
    import subprocess
    import tempfile
    from .exceptions import EditorFailure

    editor = __.os.environ.get('VISUAL') or __.os.environ.get('EDITOR') or 'nano'

    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=suffix) as tmp:
        tmp_path = tmp.name
        tmp.write(initial_text)

    try:
        result = subprocess.run([editor, tmp_path], check=True)
        if result.returncode != 0:
            raise EditorFailure(f'Editor exited with status {result.returncode}')

        with open(tmp_path, 'r', encoding='utf-8') as f:
            return f.read()
    except subprocess.SubprocessError as exc:
        raise EditorFailure('Editor process failed') from exc
    except OSError as exc:
        raise EditorFailure('Failed to read editor output') from exc
    finally:
        try: __.os.remove(tmp_path)
        except Exception as exc:
            # Log but don't fail if cleanup fails
            _scribe.warning('Failed to remove temporary file %s: %s', tmp_path, exc)
