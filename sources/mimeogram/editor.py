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
from .exceptions import MimeogramError


class EditorInterface:
    """Handles interaction with system editor."""

    @staticmethod
    def read_message(initial_text: str = '', *, suffix: str = '.md') -> str:
        """Spawn system editor to capture a message.

        Args:
            initial_text: Optional text to pre-populate the editor
            suffix: File suffix to use for syntax highlighting

        Returns:
            Text entered by user in editor

        Raises:
            MimeogramError: If editor interaction fails
        """
        # Import dependencies only when needed
        import os
        import subprocess
        import tempfile

        editor = os.environ.get('VISUAL') or os.environ.get('EDITOR') or 'nano'

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(initial_text)

        try:
            result = subprocess.run([editor, tmp_path], check=True)
            if result.returncode != 0:
                raise MimeogramError(f'Editor exited with status {result.returncode}')

            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise MimeogramError('Failed to capture message from editor') from e
        finally:
            # Import needed for removal
            import os
            try:
                os.remove(tmp_path)
            except Exception as e:
                # Log but don't fail if cleanup fails
                import logging
                logger = logging.getLogger(__name__)
                logger.warning('Failed to remove temporary file %s: %s', tmp_path, str(e))
