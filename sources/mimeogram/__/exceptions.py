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


''' Family of exceptions for package internals.

    * ``Omniexception``: Base for all internal exceptions
    * ``Omnierror``: Base for all internals errors
'''


from . import imports as __


class Omniexception( BaseException, metaclass = __.ImmutableClass ):
    ''' Base for all exceptions raised internally. '''
    # TODO: Class attribute concealment.
    # TODO: Instance attribute concealment and immutability.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised internally. '''


class AddressLocateFailure( Omnierror, LookupError ):
    ''' Failure to locate address. '''

    def __init__(
        self, subject: str, address: __.cabc.Sequence[ str ], part: str
    ):
        super( ).__init__(
            f"Could not locate part '{part}' of address '{address}' "
            f"in {subject}." )


class AsyncAssertionFailure( Omnierror, AssertionError, TypeError ):
    ''' Assertion of awaitability of entity failed. '''

    def __init__( self, entity: __.typx.Any ):
        super( ).__init__( f"Entity must be awaitable: {entity!r}" )


class EntryAssertionFailure( Omnierror, AssertionError, KeyError ):
    ''' Assertion of entry in dictionary failed. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__( f"Could not find entry '{name}' in {subject}." )


class OperationInvalidity( Omnierror, RuntimeError ):
    ''' Invalid operation. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__(
            f"Could not perform operation '{name}' on {subject}." )
