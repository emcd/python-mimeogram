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


''' Formatting of mimeogram bundles. '''


from __future__ import annotations

from . import __
from .exceptions import EmptyMimeogramError
from .acquirers import Part


class MimeogramFormatter:
    ''' Handles formatting of parts into a MIME-like bundle. '''

    @staticmethod
    def create_boundary() -> str:
        ''' Create a unique boundary marker for the mimeogram. '''
        # Import uuid only when needed
        import uuid
        return f'====MIMEOGRAM_{uuid.uuid4().hex}===='

    @staticmethod
    def format_bundle(
        parts: __.cabc.Sequence[Part],
        message: __.typx.Optional[str] = None,
        boundary: __.typx.Optional[str] = None
    ) -> str:
        ''' Format a sequence of parts into a MIME-like bundle.

            Args:
                parts: Sequence of Part objects to include in the bundle
                message: Optional message to include at the start of the bundle
                boundary: Optional custom boundary marker (generated if not provided)

            Returns:
                Formatted bundle as a string

            Raises:
                EmptyMimeogramError: If no parts and no message provided
        '''
        if not parts and message is None:
            raise EmptyMimeogramError('Cannot create an empty mimeogram (no parts and no message)')

        if boundary is None:
            boundary = MimeogramFormatter.create_boundary()

        lines = []

        if message is not None:
            lines.extend([
                f'--{boundary}',
                'Content-Location: mimeogram://editor-message',
                'Content-Type: text/plain; charset=utf-8\n',
                message.rstrip('\n')
            ])

        for part in parts:
            lines.extend([
                f'--{boundary}',
                f'Content-Location: {part.location}',
                f'Content-Type: {part.content_type}; charset={part.charset}\n',
                part.content.rstrip('\n')
            ])

        lines.append(f'--{boundary}--')
        return '\n'.join(lines)
