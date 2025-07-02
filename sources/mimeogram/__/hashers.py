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

''' Deterministic hashing utilities for mimeogram parts. '''

import hashlib
from typing import Sequence, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..parts import Part


def hash_mimeogram_parts(
    parts: 'Sequence["Part"]',
    message: Optional[str] = None
) -> str:
    ''' Computes a deterministic hash for a sequence of mimeogram parts. '''
    m = hashlib.sha256()
    if message is not None:
        m.update(message.encode('utf-8'))
    for part in parts:
        m.update(str(part.location).encode('utf-8'))
        m.update(str(part.mimetype).encode('utf-8'))
        m.update(str(part.charset).encode('utf-8'))
        m.update(str(part.linesep.name).encode('utf-8'))
        m.update(str(part.content).encode('utf-8'))
    return m.hexdigest()
