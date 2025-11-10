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


''' Content acquisition from various sources. '''


import aiofiles as _aiofiles
import httpx as _httpx

from . import __
from . import exceptions as _exceptions
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


async def acquire(
    auxdata: __.appcore.state.Globals,
    sources: __.cabc.Sequence[ str | __.Path ],
) -> __.cabc.Sequence[ _parts.Part ]:
    ''' Acquires content from multiple sources. '''
    from urllib.parse import urlparse
    options = auxdata.configuration.get( 'acquire-parts', { } )
    strict = options.get( 'fail-on-invalid', False )
    recursive = options.get( 'recurse-directories', False )
    tasks: list[ __.cabc.Coroutine[ None, None, _parts.Part ] ] = [ ]
    for source in sources:
        path = __.Path( source )
        url_parts = (
            urlparse( source ) if isinstance( source, str )
            else urlparse( str( source ) ) )
        scheme = 'file' if path.drive else url_parts.scheme
        match scheme:
            case '' | 'file':
                tasks.extend( _produce_fs_tasks( source, recursive ) )
            case 'http' | 'https':
                tasks.append( _produce_http_task( str( source ) ) )
            case _:
                raise _exceptions.UrlSchemeNoSupport( str( source ) )
    if strict: return await __.asyncf.gather_async( *tasks )
    results: tuple[ __.generics.GenericResult, ... ] = (
        await __.asyncf.gather_async(
            *tasks, return_exceptions = True
        )
    )
    # TODO: Factor into '__.generics.extract_results_filter_errors'.
    values: list[ _parts.Part ] = [ ]
    for result in results:
        if __.generics.is_error( result ):
            _scribe.warning( str( result.error ) )
            continue
        values.append( result.extract( ) )
    return tuple( values )


async def _acquire_from_file( location: __.Path ) -> _parts.Part:
    ''' Acquires content from text file. '''
    from .exceptions import ContentAcquireFailure, ContentDecodeFailure
    try:
        async with _aiofiles.open( location, 'rb' ) as f: # pyright: ignore
            content_bytes = await f.read( )
    except Exception as exc: raise ContentAcquireFailure( location ) from exc
    mimetype, charset = __.detextive.infer_mimetype_charset(
        content_bytes, location = str( location ) )
    if charset is None: raise ContentDecodeFailure( location, '???' )
    linesep = __.detextive.LineSeparators.detect_bytes( content_bytes )
    if linesep is None:
        _scribe.warning( f"No line separator detected in '{location}'." )
        linesep = __.detextive.LineSeparators( __.os.linesep )
    try:
        content = __.detextive.decode(
            content_bytes, location = str( location ) )
    except Exception as exc:
        raise ContentDecodeFailure( location, charset ) from exc
    _scribe.debug( f"Read file: {location}" )
    return _parts.Part(
        location = str( location ),
        mimetype = mimetype,
        charset = charset,
        linesep = linesep,
        content = linesep.normalize( content ) )


async def _acquire_via_http(
    client: _httpx.AsyncClient, url: str
) -> _parts.Part:
    ''' Acquires content via HTTP/HTTPS. '''
    from .exceptions import ContentAcquireFailure, ContentDecodeFailure
    try:
        response = await client.get( url )
        response.raise_for_status( )
    except Exception as exc: raise ContentAcquireFailure( url ) from exc
    http_content_type = response.headers.get( 'content-type' )
    content_bytes = response.content
    mimetype, charset = __.detextive.infer_mimetype_charset(
        content_bytes,
        location = url,
        http_content_type = http_content_type or __.absent )
    if charset is None: raise ContentDecodeFailure( url, '???' )
    linesep = __.detextive.LineSeparators.detect_bytes( content_bytes )
    if linesep is None:
        _scribe.warning( f"No line separator detected in '{url}'." )
        linesep = __.detextive.LineSeparators( __.os.linesep )
    try:
        content = __.detextive.decode(
            content_bytes,
            location = url,
            http_content_type = http_content_type or __.absent )
    except Exception as exc:
        raise ContentDecodeFailure( url, charset ) from exc
    _scribe.debug( f"Fetched URL: {url}" )
    return _parts.Part(
        location = url,
        mimetype = mimetype,
        charset = charset,
        linesep = linesep,
        content = linesep.normalize( content ) )


_files_to_ignore = frozenset( ( '.DS_Store', '.env' ) )
_directories_to_ignore = frozenset( ( '.bzr', '.git', '.hg', '.svn' ) )
def _collect_directory_files(
    directory: __.Path, recursive: bool
) -> list[ __.Path ]:
    ''' Collects and filters files from directory hierarchy. '''
    import gitignorefile
    cache = gitignorefile.Cache( )
    paths: list[ __.Path ] = [ ]
    _scribe.debug( f"Collecting files in directory: {directory}" )
    for entry in directory.iterdir( ):
        if entry.is_dir( ) and entry.name in _directories_to_ignore:
            _scribe.debug( f"Ignoring directory: {entry}" )
            continue
        if entry.is_file( ) and entry.name in _files_to_ignore:
            _scribe.debug( f"Ignoring file: {entry}" )
            continue
        if cache( str( entry ) ):
            _scribe.debug( f"Ignoring path (matched by .gitignore): {entry}" )
            continue
        if entry.is_dir( ) and recursive:
            paths.extend( _collect_directory_files( entry, recursive ) )
        elif entry.is_file( ): paths.append( entry )
    return paths


def _produce_fs_tasks(
    location: str | __.Path, recursive: bool = False
) -> tuple[ __.cabc.Coroutine[ None, None, _parts.Part ], ...]:
    location_ = __.Path( location )
    if location_.is_file( ) or location_.is_symlink( ):
        return ( _acquire_from_file( location_ ), )
    if location_.is_dir( ):
        files = _collect_directory_files( location_, recursive )
        return tuple( _acquire_from_file( f ) for f in files )
    raise _exceptions.ContentAcquireFailure( location )


def _produce_http_task(
    url: str
) -> __.cabc.Coroutine[ None, None, _parts.Part ]:
    # TODO: URL object rather than string.
    # TODO: Reuse clients for common hosts.

    async def _execute_session( ) -> _parts.Part:
        async with _httpx.AsyncClient( # nosec B113
            follow_redirects = True
        ) as client: return await _acquire_via_http( client, url )

    return _execute_session( )
