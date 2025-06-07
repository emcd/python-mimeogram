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


from . import imports as __
from . import asyncf as _asyncf


async def acquire_text_file_async(
    file: str | __.Path,
    charset: str = 'utf-8',
    deserializer: __.Absential[
        __.typx.Callable[ [ str ], __.typx.Any ] ] = __.absent,
) -> __.typx.Any:
    ''' Reads file asynchronously. '''
    from aiofiles import open as open_ # pyright: ignore
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
    return await _asyncf.gather_async(
        *(  acquire_text_file_async(
                file, charset = charset, deserializer = deserializer )
            for file in files ),
        error_message = 'Failure to read files.',
        return_exceptions = return_exceptions )
