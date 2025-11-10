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


''' Assert basic characteristics of package and modules thereof. '''


import pytest

from . import __


@pytest.mark.parametrize( 'package_name', __.PACKAGES_NAMES )
def test_000_sanity( package_name ):
    ''' Package is sane. '''
    package = __.cache_import_module( package_name )
    assert package.__package__ == package_name
    assert package.__name__ == package_name


@pytest.mark.parametrize( 'module_qname', __.MODULES_QNAMES )
def test_100_sanity( module_qname ):
    ''' Package module is sane. '''
    package_name = __.PACKAGES_NAMES_BY_MODULE_QNAME[ module_qname ]
    module = __.cache_import_module( module_qname )
    assert module.__package__ == package_name
    assert module.__name__ == module_qname
