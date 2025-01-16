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


class Omniexception( BaseException ):
    ''' Base for all exceptions raised by package API. '''
    # TODO: Class and instance attribute concealment and immutability.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


# TODO: Fix class names to comply with nomenclature standards.
# TODO: Fix docstrings to comply with coding style.


class EmptyMimeogramError( Omnierror ):
    ''' Attempt to create an empty mimeogram. '''


class ContentAcquisitionFailure( Omnierror ):
    ''' Base class for content acquisition failures. '''


class ContentReadFailure(ContentAcquisitionFailure):
    ''' Failure while reading file content. '''


class ContentFetchFailure(ContentAcquisitionFailure):
    ''' Failure while fetching URL content. '''


class FileOperationFailure(Omnierror):
    ''' Base class for file operation failures. '''


class WriteFailure(FileOperationFailure):
    ''' Failure while writing file content. '''


class ReadFailure(FileOperationFailure):
    ''' Failure while reading file content. '''


class ContentParsingFailure(Omnierror):
    ''' Failure while parsing mimeogram content. '''


class EditorFailure(Omnierror):
    ''' Failure while running or reading from editor. '''


class OperationCancelledFailure(Omnierror):
    ''' Operation cancelled by user. '''
