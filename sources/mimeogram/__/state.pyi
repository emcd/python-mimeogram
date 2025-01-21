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

# pylint: skip-file


from . import imports as __
from . import application as _application


class DirectorySpecies( __.enum.Enum ):

    Cache = ...
    Data = ...
    State = ...


@__.dataclass
class Globals:

    application: _application.Information
    directories: __.PlatformDirs

    def as_dictionary( self ) -> __.cabc.Mapping[ str, __.typx.Any ]: ...

    def provide_cache_location( self, *appendages: str ) -> __.Path: ...

    def provide_data_location( self, *appendages: str ) -> __.Path: ...

    def provide_state_location( self, *appendages: str ) -> __.Path: ...

    def provide_location(
        self, species: DirectorySpecies, *appendages: str
    ) -> __.Path: ...
