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


''' Core entities for filesystem protection. '''


from .. import __


class Reasons( __.enum.Enum ):
    ''' Reasons why location may be protected. '''

    Concealment =       'Hidden file or directory'
    Credentials =       'Credentials or secrets location'
    CustomAddition =    'User-specified custom location'
    OsDirectory =       'Operating system directory'
    PlatformSensitive = 'Platform-sensitive location'
    UserConfiguration = 'User configuration directory'
    VersionControl =    'Version control internals'


class Status( __.immut.DataclassObject ):
    ''' Protection status for location. '''

    path: __.Path
    reason: __.typx.Optional[ Reasons ] = None
    active: bool = False

    def __bool__( self ): return self.active

    @property
    def description( self ) -> str:
        ''' Human-readable description of protection. '''
        if not self.active: return 'Not protected'
        return (
            f"Protected: {self.reason.value}"
            if self.reason else 'Protected' )


class Protector(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Filesystem protection checker. '''

    @__.abc.abstractmethod
    def verify( self, path: __.Path ) -> Status:
        ''' Verifies if a path should be protected. '''
        raise NotImplementedError
