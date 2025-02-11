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


''' Mimeogram parts. '''


from __future__ import annotations

from . import __
from . import fsprotect as _fsprotect


class LineSeparators( __.enum.Enum ):
    ''' Line separators for various platforms. '''

    CR =    '\r'    # Classic MacOS
    CRLF =  '\r\n'  # DOS/Windows
    LF =    '\n'    # Unix/Linux

    @classmethod
    def detect_bytes( # pylint: disable=inconsistent-return-statements
        selfclass, content: bytes, limit = 1024
    ) -> LineSeparators | None:
        ''' Detects newline characters in bytes array. '''
        # TODO: Pyright bug? `Self` not recognized as type for enum members
        sample = content[ : limit ]
        found_cr = False
        for byte in sample:
            match byte:
                case 0xd:
                    if found_cr: return selfclass.CR
                    found_cr = True
                case 0xa: # linefeed
                    if found_cr: return selfclass.CRLF
                    return selfclass.LF
                case _:
                    if found_cr: return selfclass.CR
        return

    @classmethod
    def normalize_universal( selfclass, content: str ) -> str:
        ''' Normalizes all varieties of newline characters in text. '''
        return content.replace( '\r\n', '\r' ).replace( '\r', '\n' )

    def nativize( self, content: str ) -> str:
        ''' Nativizes specific variety newline characters in text. '''
        if LineSeparators.LF is self: return content
        return content.replace( '\n', self.value )

    def normalize( self, content: str ) -> str:
        ''' Normalizes specific variety newline characters in text. '''
        if LineSeparators.LF is self: return content
        return content.replace( self.value, '\n' )


class Resolutions( __.enum.Enum ):
    ''' Available resolutions for each part. '''

    Apply =     'apply'
    Ignore =    'ignore'


class Part(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Part of mimeogram. '''
    location: str # TODO? 'Url' class
    mimetype: str
    charset: str
    linesep: LineSeparators
    content: str

    # TODO? 'format' method
    # TODO? 'parse' method


class Target(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Target information for mimeogram part. '''
    part: Part
    destination: __.Path
    protection: _fsprotect.Status
