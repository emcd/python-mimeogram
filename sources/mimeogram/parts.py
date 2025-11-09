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


from . import __
from . import fsprotect as _fsprotect


LineSeparators = __.detextive.LineSeparators


class Resolutions( __.enum.Enum ):
    ''' Available resolutions for each part. '''

    Apply =     'apply'
    Ignore =    'ignore'


class Part( __.immut.DataclassObject ):
    ''' Part of mimeogram. '''
    location: str # TODO? 'Url' class
    mimetype: str
    charset: str
    linesep: "LineSeparators"
    content: str

    # TODO? 'format' method
    # TODO? 'parse' method


class Target( __.immut.DataclassObject ):
    ''' Target information for mimeogram part. '''
    part: Part
    destination: __.Path
    protection: _fsprotect.Status
