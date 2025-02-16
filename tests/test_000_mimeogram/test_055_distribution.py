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


''' Tests for distribution module. '''


from contextlib import AsyncExitStack
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

from . import PACKAGE_NAME, cache_import_module, create_test_files


def test_000_information_attributes( ):
    ''' Information class has expected attributes. '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )
    info = distribution.Information(
        name = 'test-dist',
        location = Path( '/test/path' ),
        editable = True )

    assert 'test-dist' == info.name
    assert Path( '/test/path' ) == info.location
    assert info.editable


def test_010_information_immutability( ):
    ''' Information class is immutable. '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )
    info = distribution.Information(
        name = 'test-dist',
        location = Path( '/test/path' ),
        editable = True )

    with pytest.raises( AttributeError ):
        info.name = 'new-name'

    with pytest.raises( AttributeError ):
        info.location = Path( '/new/path' )

    with pytest.raises( AttributeError ):
        info.editable = False


def test_020_provide_data_location( ):
    ''' Information.provide_data_location provides expected paths. '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )
    info = distribution.Information(
        name = 'test-dist',
        location = Path( '/test/path' ),
        editable = True )

    assert Path( '/test/path/data' ) == info.provide_data_location( )
    assert (
        Path( '/test/path/data/subdir/file.txt' )
        == info.provide_data_location( 'subdir', 'file.txt' ) )


@pytest.mark.asyncio
async def test_100_prepare_development( provide_tempdir ):
    ''' Information.prepare handles development environment. '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )

    # Create mock development environment
    pyproject_content = '''
[project]
name = "test-package"
version = "1.0.0"
'''
    test_files = { 'pyproject.toml': pyproject_content }

    with create_test_files( provide_tempdir, test_files ):
        async with AsyncExitStack( ) as exits:
            info = await distribution.Information.prepare(
                package = PACKAGE_NAME,
                exits = exits,
                project_anchor = provide_tempdir )

            assert info.editable
            assert 'test-package' == info.name
            assert provide_tempdir == info.location


@pytest.mark.asyncio
async def test_110_prepare_production( ):
    ''' Information.prepare handles production environment. '''
    distribution = cache_import_module( 'mimeogram.__.distribution' )

    # Mock packages_distributions to simulate installed package
    packages = { PACKAGE_NAME: [ 'test-dist' ] }
    path = Path( '/test/installed/path' )
    mock_file = MagicMock( )

    with patch(
        'importlib_metadata.packages_distributions',
        return_value = packages
    ), patch(
        'importlib_resources.files',
        return_value = mock_file
    ), patch(
        'importlib_resources.as_file'
    ), patch.object(
        AsyncExitStack,
        'enter_context',
        return_value = path
    ):
        async with AsyncExitStack( ) as exits:
            info = await distribution.Information.prepare(
                package = PACKAGE_NAME, exits = exits )

            assert not info.editable
            assert 'test-dist' == info.name
            assert path == info.location


@pytest.mark.asyncio
@pytest.mark.skipif(
    not hasattr( sys, 'oxidized' ),
    reason = "PyOxidizer tests only run in PyOxidizer environment" )
async def test_120_prepare_pyoxidizer( ):
    ''' Information.prepare handles PyOxidizer environment. '''
    # This test only runs in a PyOxidizer environment.
    # We could potentially mock the PyOxidizer environment,
    # but it would be complex and might not accurately
    # represent real PyOxidizer behavior.
