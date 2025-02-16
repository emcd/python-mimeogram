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


''' Information about package distribution. '''


from . import imports as __
from . import io as _io


class Information(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Information about a package distribution. '''

    name: str
    location: __.Path
    editable: bool

    @classmethod
    async def prepare(
        selfclass, package: str, exits: __.ExitsAsync,
        project_anchor: __.Absential[ __.Path ] = __.absent,
    ) -> __.typx.Self:
        ''' Acquires information about our package distribution. '''
        import sys
        # Detect PyInstaller bundle.
        if getattr( sys, 'frozen', False ) and hasattr( sys, '_MEIPASS' ):
            project_anchor = __.Path( getattr( sys, '_MEIPASS' ) )
        # TODO: Python 3.12: importlib.metadata
        from importlib_metadata import packages_distributions
        # https://github.com/pypa/packaging-problems/issues/609
        name = packages_distributions( ).get( package )
        if name is None: # Development sources rather than distribution.
            editable = True # Implies no use of importlib.resources.
            location, name = (
                await _acquire_development_information(
                    location = project_anchor ) )
        else:
            editable = False
            name = name[ 0 ]
            location = await _acquire_production_location( package, exits )
        return selfclass(
            editable = editable, location = location, name = name )

    def provide_data_location( self, *appendages: str ) -> __.Path:
        ''' Provides location of distribution data. '''
        base = self.location / 'data'
        if appendages: return base.joinpath( *appendages )
        return base


async def _acquire_development_information(
    location: __.Absential[ __.Path ] = __.absent
) -> tuple[ __.Path, str ]:
    from tomli import loads
    if __.is_absent( location ):
        location = __.Path( __file__ ).parents[ 3 ].resolve( strict = True )
    pyproject = await _io.acquire_text_file_async(
        location / 'pyproject.toml', deserializer = loads )
    name = pyproject[ 'project' ][ 'name' ]
    return location, name


async def _acquire_production_location(
    package: str, exits: __.ExitsAsync
) -> __.Path:
    # TODO: Python 3.12: importlib.resources
    # TODO: 'importlib_resources' PR to fix 'as_file' type signature.
    from importlib_resources import files, as_file # pyright: ignore
    # Extract package contents to temporary directory, if necessary.
    return exits.enter_context(
        as_file( files( package ) ) ) # pyright: ignore
