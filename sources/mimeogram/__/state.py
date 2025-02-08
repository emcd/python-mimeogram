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


''' Immutable global state. '''


from . import imports as __
from . import application as _application
from . import distribution as _distribution


class DirectorySpecies( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Possible species for locations. '''

    Cache = 'cache'
    Data = 'data'
    State = 'state'


class Globals(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Immutable global data. Required by some library functions. '''

    application: _application.Information
    configuration: __.AccretiveDictionary[ str, __.typx.Any ]
    directories: __.PlatformDirs
    distribution: _distribution.Information
    exits: __.ExitsAsync

    def as_dictionary( self ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Returns shallow copy of state. '''
        from dataclasses import fields
        return {
            field.name: getattr( self, field.name )
            for field in fields( self ) }

    def provide_cache_location( self, *appendages: str ) -> __.Path:
        ''' Provides cache location from configuration. '''
        return self.provide_location( DirectorySpecies.Cache, *appendages )

    def provide_data_location( self, *appendages: str ) -> __.Path:
        ''' Provides data location from configuration. '''
        return self.provide_location( DirectorySpecies.Data, *appendages )

    def provide_state_location( self, *appendages: str ) -> __.Path:
        ''' Provides state location from configuration. '''
        return self.provide_location( DirectorySpecies.State, *appendages )

    def provide_location(
        self, species: DirectorySpecies, *appendages: str
    ) -> __.Path:
        ''' Provides particular species of location from configuration. '''
        species_name = species.value
        base = getattr( self.directories, f"user_{species_name}_path" )
        spec = self.configuration.get( 'locations', { } ).get( species_name )
        if spec:
            args: dict[ str, str | __.Path ] = {
                f"user_{species_name}": base,
                'user_home': __.Path.home( ),
                'application_name': self.application.name,
            }
            base = __.Path( spec.format( **args ) )
        if appendages: return base.joinpath( *appendages )
        return base
