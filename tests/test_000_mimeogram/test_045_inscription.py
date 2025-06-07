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


''' Tests for inscription module. '''


import builtins
import logging

import pytest

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture( autouse = True )
def reset_icecream( ):
    ''' Reset Icecream state before each test. '''
    import icecream
    icecream.install( )  # Reset to defaults
    icecream.ic.enable( )  # Ensure enabled initially
    yield
    # Cleanup by removing ic from builtins if it exists
    if hasattr( builtins, 'ic' ):
        delattr( builtins, 'ic' )


@pytest.fixture( autouse = True )
def reset_logging( ):
    ''' Reset logging state before each test. '''
    scribe = logging.getLogger( PACKAGE_NAME )
    scribe.handlers.clear( )
    scribe.propagate = False
    scribe.setLevel( logging.NOTSET )
    yield


def test_000_modes( ):
    ''' Mode enumeration has expected values. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    assert 'null' == inscription.Modes.Null.value
    assert 'pass' == inscription.Modes.Pass.value
    assert 'rich' == inscription.Modes.Rich.value


def test_100_control_defaults( ):
    ''' Control class has expected defaults. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( )
    assert inscription.Modes.Null == control.mode
    assert control.level is None


def test_200_prepare_scribe_logging_null( provide_tempenv ):
    ''' Null mode configures minimal logging. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Null )
    inscription.prepare_scribe_logging( control )

    scribe = logging.getLogger( PACKAGE_NAME )
    assert not scribe.propagate
    assert logging.INFO == scribe.level
    assert 1 == len( scribe.handlers )
    assert isinstance( scribe.handlers[ 0 ], logging.NullHandler )


def test_210_prepare_scribe_logging_pass( provide_tempenv ):
    ''' Pass mode propagates logs to root logger. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Pass )
    inscription.prepare_scribe_logging( control )

    scribe = logging.getLogger( PACKAGE_NAME )
    assert scribe.propagate
    assert logging.INFO == scribe.level
    assert 0 == len( scribe.handlers )


def test_220_prepare_scribe_logging_rich( provide_tempenv ):
    ''' Rich mode configures Rich logging handler. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Rich )
    inscription.prepare_scribe_logging( control )

    scribe = logging.getLogger( PACKAGE_NAME )
    assert not scribe.propagate
    assert logging.INFO == scribe.level
    assert 1 == len( scribe.handlers )

    from rich.logging import RichHandler
    handler = scribe.handlers[ 0 ]
    assert isinstance( handler, RichHandler )
    assert handler.rich_tracebacks

    formatter = handler.formatter
    assert isinstance( formatter, logging.Formatter )
    assert "%(name)s: %(message)s" == formatter._fmt


def test_230_prepare_scribe_logging_level( provide_tempenv ):
    ''' Logger level can be configured. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( level = 'debug' )
    inscription.prepare_scribe_logging( control )

    scribe = logging.getLogger( PACKAGE_NAME )
    assert logging.DEBUG == scribe.level


def test_240_prepare_scribe_logging_level_from_env( provide_tempenv ):
    ''' Logger level can be configured from environment. '''
    provide_tempenv[ f"{PACKAGE_NAME.upper( )}_LOG_LEVEL" ] = 'DEBUG'
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( )
    inscription.prepare_scribe_logging( control )

    scribe = logging.getLogger( PACKAGE_NAME )
    assert logging.DEBUG == scribe.level


def test_300_prepare_scribe_icecream_null( provide_tempenv ):
    ''' Null mode disables Icecream. '''
    # Setup development mode to enable Icecream first
    provide_tempenv[ '_DEVELOPMENT_MODE_' ] = 'TRUE'
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Null )
    inscription.prepare_scribe_icecream( control )

    import icecream
    assert not icecream.ic.enabled


def test_310_prepare_scribe_icecream_pass( provide_tempenv ):
    ''' Pass mode enables standard Icecream. '''
    # Setup development mode
    provide_tempenv[ '_DEVELOPMENT_MODE_' ] = 'TRUE'
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Pass )
    inscription.prepare_scribe_icecream( control )

    import icecream
    assert icecream.ic.enabled
    assert icecream.ic.includeContext
    assert 'DEBUG    ' == icecream.ic.prefix


def test_320_prepare_scribe_icecream_rich( provide_tempenv ):
    ''' Rich mode enables Rich-formatted Icecream. '''
    # Setup development mode
    provide_tempenv[ '_DEVELOPMENT_MODE_' ] = 'TRUE'
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Rich )
    inscription.prepare_scribe_icecream( control )

    import icecream
    assert icecream.ic.enabled
    assert icecream.ic.includeContext
    assert 'DEBUG    ' == icecream.ic.prefix

    from rich.pretty import pretty_repr
    assert pretty_repr == icecream.ic.argToStringFunction


def test_330_prepare_scribe_icecream_no_development( provide_tempenv ):
    ''' Icecream is disabled without development mode. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )
    control = inscription.Control( mode = inscription.Modes.Pass )
    inscription.prepare_scribe_icecream( control )

    assert hasattr( builtins, 'ic' )
    result = builtins.ic( 'test' )
    assert ( 'test', ) == result


def test_400_prepare( provide_tempenv ):
    ''' prepare configures both logging and Icecream. '''
    inscription = cache_import_module( 'mimeogram.__.inscription' )

    # Test each mode to ensure full coverage
    for mode in inscription.Modes:
        # Set development mode for Icecream
        provide_tempenv[ '_DEVELOPMENT_MODE_' ] = 'TRUE'

        # Reset logger for this test iteration
        scribe = logging.getLogger( PACKAGE_NAME )
        scribe.handlers.clear( )
        scribe.propagate = False
        scribe.setLevel( logging.NOTSET )

        # Test the mode
        control = inscription.Control( mode = mode )
        inscription.prepare( control )

        # Verify logger configuration
        match mode:
            case inscription.Modes.Null:
                assert isinstance( scribe.handlers[ 0 ], logging.NullHandler )
            case inscription.Modes.Pass:
                assert scribe.propagate
            case inscription.Modes.Rich:
                from rich.logging import RichHandler
                assert isinstance( scribe.handlers[ 0 ], RichHandler )
            case _:
                pytest.fail( f"Unexpected mode: {mode}" )  # pragma: no cover
