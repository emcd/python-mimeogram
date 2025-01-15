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
from .acquirers import Part
from .exceptions import EmptyMimeogramError


_scribe = __.produce_scribe(__name__)


def create_boundary() -> str:
    """Create a unique boundary marker."""
    import uuid
    return f'====MIMEOGRAM_{uuid.uuid4().hex}===='


def format_part(
    part: Part,
    boundary: str,
    is_last: bool = False
) -> str:
    """Format a single part with headers."""
    headers = [
        f'--{boundary}',
        f'Content-Location: {part.location}',
        f'Content-Type: {part.content_type}; charset={part.charset}\n'
    ]

    if is_last:
        return '\n'.join(headers + [part.content.rstrip('\n')])
    return '\n'.join(headers + [part.content])


def format_message(
    message: str,
    boundary: str
) -> str:
    """Format an editor message as a part."""
    headers = [
        f'--{boundary}',
        'Content-Location: mimeogram://editor-message',
        'Content-Type: text/plain; charset=utf-8\n'
    ]
    return '\n'.join(headers + [message.rstrip('\n')])


def format_bundle(
    parts: __.cabc.Sequence[Part],
    message: __.typx.Optional[str] = None,
    boundary: __.typx.Optional[str] = None
) -> str:
    """Format parts into a MIME-like bundle."""
    if not parts and message is None:
        raise EmptyMimeogramError('Cannot create an empty mimeogram')

    if boundary is None:
        boundary = create_boundary()

    lines = []

    if message is not None:
        lines.append(format_message(message, boundary))

    for i, part in enumerate(parts):
        lines.append(format_part(part, boundary, i == len(parts) - 1))

    lines.append(f'--{boundary}--')
    return '\n'.join(lines)
