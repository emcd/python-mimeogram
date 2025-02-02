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


''' Common I/O primitives. '''


from aiofiles.threadpool.text import (
    AsyncTextIOWrapper as _AiofilesTextWrapper,
)

from . import imports as __
from . import asyncf as _asyncf
from . import generics as _generics


async def acquire_text_file_async(
    file: str | __.Path,
    charset: str = 'utf-8',
    deserializer: __.Absential[
        __.typx.Callable[ [ str ], __.typx.Any ] ] = __.absent,
) -> __.typx.Any:
    ''' Reads file asynchronously. '''
    from aiofiles import open as open_
    async with open_( file, encoding = charset ) as stream:
        data = await stream.read( )
    if not __.is_absent( deserializer ):
        return deserializer( data )
    return data


async def acquire_text_files_async(
    *files: str | __.Path,
    charset: str = 'utf-8',
    deserializer: __.Absential[
        __.typx.Callable[ [ str ], __.typx.Any ] ] = __.absent,
    return_exceptions: bool = False
) -> __.typx.Sequence[ __.typx.Any ]:
    ''' Reads files in parallel asynchronously. '''
    # TODO? Batch to prevent fd exhaustion over large file sets.
    from aiofiles import open as open_
    extractor = _result_extractor if return_exceptions else _bare_extractor
    async with __.ExitsAsync( ) as exits:
        streams = await _asyncf.gather_async(
            *(  exits.enter_async_context( open_( file, encoding = charset ) )
                for file in files ),
            return_exceptions = return_exceptions )
        data = await _asyncf.gather_async(
            *( extractor( stream ) for stream in streams ),
            return_exceptions = return_exceptions,
            ignore_nonawaitables = return_exceptions )
    if not __.is_absent( deserializer ):
        transformer = (
            _produce_result_transformer( deserializer ) if return_exceptions
            else _produce_bare_transformer( deserializer ) )
        return tuple( transformer( datum ) for datum in data )
    return data


def _bare_extractor( stream: _AiofilesTextWrapper ) -> __.typx.Any:
    return stream.read( )


def _produce_bare_transformer(
    deserializer: __.typx.Callable[ [ str ], __.typx.Any ]
) -> __.typx.Callable[ [ __.typx.Any ], __.typx.Any ]:
    def transformer( datum: __.typx.Any ) -> __.typx.Any:
        return deserializer( datum )
    return transformer


def _result_extractor( result: _generics.GenericResult ) -> __.typx.Any:
    return result.extract( ).read( ) if result.is_value( ) else result


def _produce_result_transformer(
    deserializer: __.typx.Callable[ [ str ], __.typx.Any ]
) -> __.typx.Callable[ [ _generics.GenericResult ], _generics.GenericResult ]:
    def transformer(
        result: _generics.Result[ __.typx.Any, Exception ]
    ) -> _generics.Result[ __.typx.Any, Exception ]:
        return result.transform( deserializer )
    return transformer
