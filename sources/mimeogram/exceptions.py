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


''' Family of exceptions for package API.

    * ``Omniexception``: Base for all package exceptions
    * ``Omnierror``: Base for all package errors
'''


from . import __


class Omniexception( BaseException, metaclass = __.ImmutableClass ):
    ''' Base for all exceptions raised by package API. '''
    # TODO: Class attribute concealment.
    # TODO: Instance attribute concealment and immutability.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class ContentAcquireFailure( Omnierror ):
    ''' Failure to acquire content from location. '''

    def __init__( self, location: str | __.Path ):
        super( ).__init__( f"Could not acquire content from '{location}'." )


class ContentDecodeFailure( Omnierror ):
    ''' Failure to decode content as character set from location. '''

    def __init__( self, location: str | __.Path, charset: str ):
        super( ).__init__(
            f"Could not decode content at '{location}' "
            f"as character set '{charset}'." )


class ContentUpdateFailure( Omnierror ):
    ''' Failure to update content at location. '''

    def __init__( self, location: str | __.Path ):
        super( ).__init__( f"Could not update content at '{location}'." )


class DifferencesProcessFailure( Omnierror ):
    ''' Failure during diff processing. '''

    def __init__( self, reason: str ):
        super( ).__init__( f"Could not process changes. Reason: {reason}" )


class EditorFailure( Omnierror ):
    ''' Failure while operating editor. '''

    def __init__( self, cause: str | Exception ):
        super( ).__init__( f"Could not edit content. Cause: {cause}" )


class LocationInvalidity( Omnierror ):
    ''' Invalid location. '''

    def __init__( self, location: str | __.Path ):
        super( ).__init__( f"Invalid location '{location}'." )


class MimeogramFormatEmpty( Omnierror ):
    ''' Attempt to format empty mimeogram. '''

    def __init__( self ):
        super( ).__init__( "Cannot format empty mimeogram." )


class MimeogramParseFailure( Omnierror ):
    ''' Failure to parse mimeogram content. '''

    def __init__( self, reason: str ):
        super( ).__init__( f"Could not parse mimeogram. Reason: {reason}" )


class PagerFailure( Omnierror ):
    ''' Failure while operating pager. '''

    def __init__( self, cause: str | Exception ):
        super( ).__init__( f"Could not display content. Cause: {cause}" )


class ProgramAbsenceError( Omnierror ):
    ''' Could not discover valid editor. '''

    def __init__( self, species: str ):
        super( ).__init__( f"Could not discover valid {species}." )


class TextualMimetypeInvalidity( Omnierror ):
    ''' Invalid textual MIME type for content at location. '''

    def __init__( self, location: str | __.Path, mimetype: str ):
        super( ).__init__(
            f"Invalid MIME type '{mimetype}' for content at '{location}'." )


class UrlSchemeNoSupport( Omnierror ):
    ''' Unsupported URL scheme. '''

    def __init__( self, url: str ):
        super( ).__init__( f"Scheme of URL '{url}' is not supported." )


class UserOperateCancellation( Omniexception ):
    ''' Operation cancelled by user. '''

    def __init__( self, cause: BaseException ):
        super( ).__init__( f"Operation cancelled by user. Cause: {cause}" )
