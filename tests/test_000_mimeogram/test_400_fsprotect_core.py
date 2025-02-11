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


''' Tests for filesystem protection core functionality. '''


from pathlib import Path

import pytest

from . import PACKAGE_NAME, cache_import_module


def test_100_reasons_completeness( ):
    ''' All expected protection reasons are defined. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    expected = {
        'Concealment',
        'Credentials',
        'CustomAddition',
        'OsDirectory',
        'PlatformSensitive',
        'UserConfiguration',
        'VersionControl',
    }
    actual = { reason.name for reason in core.Reasons }
    assert expected == actual, 'Missing or unexpected protection reasons'


def test_110_reasons_values( ):
    ''' Protection reasons have meaningful descriptions. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    # Check specific description patterns
    value_patterns = {
        'Concealment': 'Hidden file',
        'Credentials': 'Credentials or secrets',
        'CustomAddition': 'User-specified',
        'OsDirectory': 'Operating system',
        'PlatformSensitive': 'Platform-sensitive',
        'UserConfiguration': 'User configuration',
        'VersionControl': 'Version control',
    }
    for reason, pattern in value_patterns.items( ):
        value = core.Reasons[ reason ].value
        assert pattern in value, f"Unexpected description for {reason}"


def test_200_status_initialization( ):
    ''' Protection status properly initializes with various arguments. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    test_path = Path( '/test/path' )

    # Test default initialization
    status = core.Status( path = test_path )
    assert status.path == test_path
    assert status.reason is None
    assert not status.active

    # Test full initialization
    status = core.Status(
        path = test_path,
        reason = core.Reasons.Credentials,
        active = True )
    assert status.path == test_path
    assert status.reason == core.Reasons.Credentials
    assert status.active


def test_210_status_bool_conversion( ):
    ''' Boolean conversion reflects active status. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    test_path = Path( '/test/path' )

    # Test inactive status
    status = core.Status( path = test_path, active = False )
    assert not bool( status )

    # Test active status
    status = core.Status( path = test_path, active = True )
    assert bool( status )


def test_220_status_description_inactive( ):
    ''' Description properly formatted for inactive status. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    status = core.Status( path = Path( '/test/path' ) )
    assert status.description == 'Not protected'


def test_230_status_description_active( ):
    ''' Description properly formatted for active status with reason. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    test_path = Path( '/test/path' )

    # Test with reason
    status = core.Status(
        path = test_path,
        reason = core.Reasons.Credentials,
        active = True )
    assert status.description == 'Protected: Credentials or secrets location'

    # Test without reason
    status = core.Status( path = test_path, active = True )
    assert status.description == 'Protected'


def test_240_status_immutability( ):
    ''' Status objects are immutable. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    status = core.Status( path = Path( '/test/path' ) )

    with pytest.raises( AttributeError ):
        status.path = Path( '/other/path' )

    with pytest.raises( AttributeError ):
        status.reason = core.Reasons.Credentials

    with pytest.raises( AttributeError ):
        status.active = True


def test_250_status_hashable( ):
    ''' Status objects can be used in sets and as dictionary keys. '''
    core = cache_import_module( f"{PACKAGE_NAME}.fsprotect.core" )

    test_path = Path( '/test/path' )
    status1 = core.Status( path = test_path )
    status2 = core.Status( path = test_path )

    # Test set operations
    status_set = { status1, status2 }
    assert len( status_set ) == 1

    # Test dictionary operations
    status_dict = { status1: 'value' }
    assert status_dict[ status2 ] == 'value'
