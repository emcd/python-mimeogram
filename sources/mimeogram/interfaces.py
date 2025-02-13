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


''' Abstract bases and interfaces. '''


from __future__ import annotations

from . import __
from . import parts as _parts


class CliCommand( # pylint: disable=invalid-metaclass
    __.typx.Protocol,
    metaclass = __.ImmutableStandardProtocolDataclass,
    decorators = ( __.standard_dataclass, __.typx.runtime_checkable ),
):
    ''' CLI command. '''

    @__.abc.abstractmethod
    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command with global state. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    def provide_configuration_edits( self ) -> __.DictionaryEdits:
        ''' Provides edits against configuration from options. '''
        raise NotImplementedError


class DifferencesDisplay( # pylint: disable=invalid-metaclass
    __.typx.Protocol,
    metaclass = __.ImmutableStandardProtocolDataclass,
    decorators = ( __.standard_dataclass, __.typx.runtime_checkable ),
):
    ''' Configuration for content differences display. '''

    context_lines: int = 3
    inline_threshold: int = 24 # TODO? Adjust to terminal height.
    # TODO: colorize: bool = False
    # TODO: emojify: bool = False
    # TODO: show_whitespace: bool = False
    # TODO: truncate_lines: bool = False
    # TODO: wrap_lines: bool = False

    @__.abc.abstractmethod
    async def __call__( self, lines: __.cabc.Sequence[ str ] ) -> None:
        ''' Displays differences segment. '''
        raise NotImplementedError


class DifferencesInteractor( # pylint: disable=invalid-metaclass
    __.typx.Protocol,
    metaclass = __.ImmutableProtocolClass,
):
    ''' Interactions with content differences. '''

    @__.abc.abstractmethod
    async def __call__(
        self, lines: __.cabc.Sequence[ str ], display: DifferencesDisplay
    ) -> bool:
        ''' Prompts for action on differences segment. '''
        raise NotImplementedError


class PartInteractor( # pylint: disable=invalid-metaclass
    __.typx.Protocol,
    metaclass = __.ImmutableStandardProtocolDataclass,
    decorators = ( __.standard_dataclass, __.typx.runtime_checkable ),
):
    ''' Interactions with mimeogram parts. '''

    @__.abc.abstractmethod
    async def __call__(
        self, target: _parts.Target
    ) -> tuple[ _parts.Resolutions, str ]:
        ''' Prompts for action on mimeogram part. '''
        raise NotImplementedError
