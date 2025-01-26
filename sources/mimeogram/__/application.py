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


''' Information about application. '''


from . import imports as __


# # Note: We reuse a fixed execution ID across instances of this class
# #       which are default arguments to various preparation functions.
# #       This is done to improve import times with the understanding
# #       that not more than one execution ID should be needed during
# #       the lifetime of the process importing the library.
# _execution_id = __.uuid4( ).urn


class Information(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, )
):
    ''' Information about an application. '''

    name: __.typx.Annotated[
        str,
        __.typx.Doc( "For derivation of platform directories." ),
    ] = __.package_name
    publisher: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc( "For derivation of platform directories." ),
        __.tyro.conf.Suppress,
    ] = None
    version: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.typx.Doc( "For derivation of platform directories." ),
        __.tyro.conf.Suppress,
    ] = None
    # execution_id: __.typx.Annotated[
    #     __.typx.Optional[ str ],
    #     __.typx.Doc( "For telemetry, etc..." ),
    # ] = _execution_id

    def produce_platform_directories( self ) -> __.PlatformDirs:
        ''' Produces platform directories object for application. '''
        arguments = __.AccretiveDictionary( dict(
            appname = self.name, ensure_exists = True ) )
        if self.publisher: arguments[ 'appauthor' ] = self.publisher
        if self.version: arguments[ 'version' ] = self.version
        return __.PlatformDirs( **arguments ) # type: ignore
