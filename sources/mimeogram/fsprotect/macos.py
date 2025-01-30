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


''' Sensitive filesystem locations on macOS. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


def discover_system_paths( ) -> frozenset[ __.Path ]:
    ''' Discovers system paths. '''
    return frozenset( (
        __.Path( '/System' ),
        __.Path( '/Library' ),
        __.Path( '/usr/bin' ),
        __.Path( '/usr/local/bin' ),
    ) )


def discover_user_paths( ) -> frozenset[ __.Path ]:
    ''' Discovers user-specific paths. '''
    home = __.Path.home( )
    return frozenset( (
        home / 'Library',
        home / 'Library/Application Support',
        home / 'Library/Preferences',
        home / 'Library/Keychains',
        home / 'Library/Containers',
    ) )
