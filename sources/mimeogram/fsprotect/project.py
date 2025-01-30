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


''' Sensitive filesystem locations relative to project directory. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


def discover_sensitive_locations( ) -> frozenset[ str ]:
    ''' Discovers sensitive directories in project context. '''
    return frozenset( (
        # Version Control
        '.git', '.svn', '.hg', '.bzr',
        # Project Config
        '.idea', '.vscode', '.eclipse',
        # Build and Dependencies
        'node_modules', '.virtualenv', '.env',
        # Infrastructure
        '.terraform', '.ansible',
        # Secrets
        '.secrets', '.env',
    ) )
