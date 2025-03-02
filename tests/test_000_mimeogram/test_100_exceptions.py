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


''' Tests for public exceptions module. '''


from pathlib import Path

import pytest

from . import PACKAGE_NAME, cache_import_module


def test_000_base_exception_hierarchy( ):
    ''' Base exception hierarchy relationships. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    assert issubclass( exceptions.Omniexception, BaseException )
    assert issubclass( exceptions.Omnierror, exceptions.Omniexception )
    assert issubclass( exceptions.Omnierror, Exception )


def test_010_base_exceptions_immutability( ):
    ''' Immutability of base exception classes. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    with pytest.raises( AttributeError ):
        exceptions.Omniexception.new_attr = 'value'
    with pytest.raises( AttributeError ):
        exceptions.Omnierror.new_attr = 'value'


def test_020_content_acquisition_failures( ):
    ''' Content acquisition failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    location = Path( '/test/path' )
    exc = exceptions.ContentAcquireFailure( location )
    assert isinstance( exc, exceptions.Omnierror )
    assert str( location ) in str( exc )

    charset = 'utf-8'
    exc = exceptions.ContentDecodeFailure( location, charset )
    assert isinstance( exc, exceptions.Omnierror )
    assert str( location ) in str( exc )
    assert charset in str( exc )


def test_030_content_update_failures( ):
    ''' Content update failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    location = Path( '/test/path' )
    exc = exceptions.ContentUpdateFailure( location )
    assert isinstance( exc, exceptions.Omnierror )
    assert str( location ) in str( exc )


def test_040_differences_failures( ):
    ''' Difference processing failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    reason = 'test reason'
    exc = exceptions.DifferencesProcessFailure( reason )
    assert isinstance( exc, exceptions.Omnierror )
    assert reason in str( exc )


def test_050_editor_and_pager_failures( ):
    ''' Editor and pager failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    cause = 'test cause'
    exc = exceptions.EditorFailure( cause )
    assert isinstance( exc, exceptions.Omnierror )
    assert cause in str( exc )

    exc = exceptions.PagerFailure( cause )
    assert isinstance( exc, exceptions.Omnierror )
    assert cause in str( exc )


def test_060_location_invalidity( ):
    ''' Location invalidity exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    location = Path( '/test/path' )
    exc = exceptions.LocationInvalidity( location )
    assert isinstance( exc, exceptions.Omnierror )
    assert str( location ) in str( exc )


def test_070_mimeogram_format_failures( ):
    ''' Mimeogram format failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    exc = exceptions.MimeogramFormatEmpty( )
    assert isinstance( exc, exceptions.Omnierror )
    assert 'empty' in str( exc ).lower( )

    reason = 'test reason'
    exc = exceptions.MimeogramParseFailure( reason )
    assert isinstance( exc, exceptions.Omnierror )
    assert reason in str( exc )


def test_080_mimetype_failures( ):
    ''' MIME type failure exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    location = Path( '/test/path' )
    mimetype = 'application/octet-stream'
    exc = exceptions.TextualMimetypeInvalidity( location, mimetype )
    assert isinstance( exc, exceptions.Omnierror )
    assert str( location ) in str( exc )
    assert mimetype in str( exc )


def test_090_program_absence( ):
    ''' Program absence error exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    species = 'editor'
    exc = exceptions.ProgramAbsenceError( species )
    assert isinstance( exc, exceptions.Omnierror )
    assert species in str( exc )


def test_100_validate_tokenizer_variant_invalidity( ):
    ''' TokenizerVariantInvalidity contains correct details. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    name = "tiktoken"
    variant = "invalid_variant"
    exc = exceptions.TokenizerVariantInvalidity( name, variant )
    assert isinstance( exc, exceptions.Omnierror )
    assert name in str( exc )
    assert variant in str( exc )


def test_110_url_scheme_support( ):
    ''' URL scheme support exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    url = 'ftp://example.com'
    exc = exceptions.UrlSchemeNoSupport( url )
    assert isinstance( exc, exceptions.Omnierror )
    assert url in str( exc )


def test_120_user_operation_cancellation( ):
    ''' User operation cancellation exceptions. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    cause = KeyboardInterrupt( )
    exc = exceptions.UserOperateCancellation( cause )
    assert isinstance( exc, exceptions.Omniexception )
    assert not isinstance( exc, exceptions.Omnierror )
    assert str( cause ) in str( exc )


def test_200_exception_chaining( ):
    ''' Exception chaining behavior. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    try:
        try: raise ValueError( 'Original error' )
        except ValueError as exc:
            raise exceptions.ContentAcquireFailure( '/test' ) from exc
    except exceptions.ContentAcquireFailure as exc:
        assert isinstance( exc.__cause__, ValueError )
        assert 'Original error' in str( exc.__cause__ )


def test_210_visible_attributes( ):
    ''' Visibility of exception attributes. '''
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )

    cause = ValueError( 'test cause' )
    exc = exceptions.Omniexception( )
    exc.__cause__ = cause
    assert hasattr( exc, '__cause__' )
    assert exc.__cause__ is cause

    exc = exceptions.ContentAcquireFailure( '/test' )
    exc.__cause__ = cause
    assert hasattr( exc, '__cause__' )
    assert exc.__cause__ is cause
