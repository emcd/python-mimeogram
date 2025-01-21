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
from . import acquirers as _acquirers


def format_bundle(
    parts: __.cabc.Sequence[ _acquirers.Part ],
    message: __.typx.Optional[ str ] = None,
) -> str:
    ''' Formats parts into mimeogram. '''
    if not parts and message is None:
        from .exceptions import MimeogramFormatEmpty
        raise MimeogramFormatEmpty( )
    boundary = "====MIMEOGRAM_{uuid}====".format( uuid = __.uuid4( ).hex )
    lines: list[ str ] = [ ]
    if message:
        message_part = _acquirers.Part(
            location = 'mimeogram://message',
            mimetype = 'text/plain', # TODO? Markdown
            charset = 'utf-8',
            content = message )
        lines.append( format_part( message_part, boundary ) )
    for part in parts:
        lines.append( format_part( part, boundary ) )
    lines.append( f"--{boundary}--" )
    return '\n'.join( lines )


def format_part( part: _acquirers.Part, boundary: str ) -> str:
    ''' Formats part with boundary marker and headers. '''
    return '\n'.join( (
        f"--{boundary}",
        f"Content-Location: {part.location}",
        f"Content-Type: {part.mimetype}; charset={part.charset}",
        '',
        part.content ) )
