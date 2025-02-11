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


''' Tests for filesystem protection location discovery. '''


from . import PACKAGE_NAME, cache_import_module


def test_100_home_locations_type( ):
    ''' Home sensitive locations returns frozen set. '''
    home = cache_import_module( f"{PACKAGE_NAME}.fsprotect.home" )
    locations = home.discover_sensitive_locations( )
    assert isinstance( locations, frozenset )
    assert all( isinstance( path, str ) for path in locations )


def test_200_project_locations_type( ):
    ''' Project sensitive locations returns frozen set. '''
    project = cache_import_module( f"{PACKAGE_NAME}.fsprotect.project" )
    locations = project.discover_sensitive_locations( )
    assert isinstance( locations, frozenset )
    assert all( isinstance( path, str ) for path in locations )
