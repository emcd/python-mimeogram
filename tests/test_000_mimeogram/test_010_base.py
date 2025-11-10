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


''' Assert correct function of common imports. '''


import pytest

from . import __


@pytest.mark.parametrize(
    'module_name', ( 'cabc', 'types', 'typx' )
)
def test_100_exports( module_name ):
    ''' Module exports expected names. '''
    module = __.cache_import_module( f"{__.PACKAGE_NAME}.__.imports" )
    assert hasattr( module, module_name )
