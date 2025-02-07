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


''' Package of tests.

    Common imports, constants, and utilities for tests.
'''


import types

from types import MappingProxyType as DictionaryProxy


PACKAGE_NAME = 'mimeogram'
PACKAGES_NAMES = ( PACKAGE_NAME, )


_modules_cache: dict[ str, types.ModuleType ] = { }
def cache_import_module( qname: str ) -> types.ModuleType:
    ''' Imports module from package by name and caches it. '''
    from importlib import import_module
    package_name, *maybe_module_name = qname.rsplit( '.', maxsplit = 1 )
    if not maybe_module_name: arguments = ( qname, )
    else: arguments = ( f".{maybe_module_name[0]}", package_name, )
    if qname not in _modules_cache:
        _modules_cache[ qname ] = import_module( *arguments )
    return _modules_cache[ qname ]


def _discover_module_names( package_name: str ) -> tuple[ str, ... ]:
    from pathlib import Path
    package = cache_import_module( package_name )
    return tuple(
        path.stem
        for path in Path( package.__file__ ).parent.glob( '*.py' )
        if      path.name not in ( '__init__.py', '__main__.py' )
            and path.is_file( ) )


MODULES_NAMES_BY_PACKAGE_NAME = DictionaryProxy( {
    name: _discover_module_names( name ) for name in PACKAGES_NAMES } )
PACKAGES_NAMES_BY_MODULE_QNAME = DictionaryProxy( {
    f"{subpackage_name}.{module_name}": subpackage_name
    for subpackage_name in PACKAGES_NAMES
    for module_name in MODULES_NAMES_BY_PACKAGE_NAME[ subpackage_name ] } )
MODULES_QNAMES = tuple( PACKAGES_NAMES_BY_MODULE_QNAME.keys( ) )
MODULES_NAMES_BY_MODULE_QNAME = DictionaryProxy( {
    name: name.rsplit( '.', maxsplit = 1 )[ -1 ]
    for name in PACKAGES_NAMES_BY_MODULE_QNAME.keys( ) } )
