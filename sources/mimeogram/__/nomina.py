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


''' Common names and type aliases. '''


from . import imports as __


ComparisonResult: __.typx.TypeAlias = bool | __.types.NotImplementedType
NominativeArguments: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]
PositionalArguments: __.typx.TypeAlias = __.cabc.Sequence[ __.typx.Any ]

NominativeDictionary: __.typx.TypeAlias = (
    __.cabc.MutableMapping[ str, __.typx.Any ] )
ImmutableNominativeDictionary: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, __.typx.Any ] )


package_name = __name__.split( '.', maxsplit = 1 )[ 0 ]
