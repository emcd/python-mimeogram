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
        if hasattr( sys, 'oxidized' ): # PyOxidizer
            location, name = (
                await _acquire_pyoxidizer_information( package, exits ) )
            return selfclass(
                editable = False, location = location, name = name )
        from importlib.metadata import packages_distributions
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
    # TODO: 'importlib_resources' PR to fix 'as_file' type signature.
    # TODO: Python 3.12: importlib.resources
    from importlib_resources import files, as_file # type: ignore
    # Extract package contents to temporary directory, if necessary.
    return exits.enter_context(
        as_file( files( package ) ) ) # type: ignore


async def _acquire_pyoxidizer_information( # pylint: disable=too-many-locals
    package: str, exits: __.ExitsAsync
) -> tuple[ __.Path, str ]:
    import oxidized_importer
    import sys
    import tempfile
    finder = next(
        finder for finder in sys.meta_path
        if isinstance( finder, oxidized_importer.OxidizedFinder ) ) # pyright: ignore
    distribution = oxidized_importer.OxidizedDistribution.from_name( package ) # pyright: ignore
    tmpdir = exits.enter_context( tempfile.TemporaryDirectory( ) ) # pylint: disable=consider-using-with
    location = __.Path( tmpdir )
    reader = finder.get_resource_reader( package ) # pyright: ignore
    for resource in reader.contents( ): # pyright: ignore
        content = reader.open_resource( resource ).read( ) # pyright: ignore
        resource_ = location / resource # pyright: ignore
        resource_.parent.mkdir( parents = True, exist_ok = True ) # pyright: ignore
        resource_.write_bytes( content ) # pyright: ignore
    return location, distribution.name # pyright: ignore
