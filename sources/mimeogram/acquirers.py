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


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


@__.dataclass
class Part:
    ''' Part of mimeogram. '''
    location: str
    content: str
    mimetype: str
    charset: str = 'utf-8'


async def acquire(
    sources: __.cabc.Sequence[ str | __.Path ],
    recursive: bool = False,
    # strict: bool = False,
) -> __.cabc.Sequence[ Part ]:
    ''' Acquires content from multiple sources. '''
    from urllib.parse import urlparse
    tasks: list[ __.cabc.Coroutine[ None, None, Part ] ] = [ ]
    for source in sources:
        url_parts = (
            urlparse( source ) if isinstance( source, str )
            else urlparse( str( source ) ) )
        match url_parts.scheme:
            case '' | 'file':
                tasks.extend( _produce_fs_tasks( source, recursive ) )
            case 'http' | 'https':
                tasks.append( _produce_http_task( str( source ) ) )
            case _:
                pass # TODO: Raise exception for unsupported URL scheme.
    return await __.gather_async( *tasks )


async def _acquire_from_file( path: __.Path ) -> Part:
    ''' Acquires content from text file. '''
    from .exceptions import ContentAcquireFailure
    try:
        async with __.aiofiles.open( path, 'r' ) as f:
            content = await f.read( )
    except Exception as exc: raise ContentAcquireFailure( path ) from exc
    mimetype = _discover_mimetype( content.encode( ), path )
    _scribe.debug( f"Read file: {path}" )
    return Part(
        location = str( path ), mimetype = mimetype, content = content )


async def _acquire_via_http( client: __.httpx.AsyncClient, url: str ) -> Part:
    ''' Acquires content via HTTP/HTTPS. '''
    from .exceptions import ContentAcquireFailure, ContentDecodeFailure
    try:
        response = await client.get( url )
        response.raise_for_status( )
    except Exception as exc: raise ContentAcquireFailure( url ) from exc
    mimetype = (
        response.headers.get( 'content-type', 'application/octet-stream' )
        .split( ';' )[ 0 ].strip( ) )
    content_bytes = response.content
    if not _is_textual_mime( mimetype ):
        mimetype = _discover_mimetype( content_bytes, url )
    charset = response.encoding or 'utf-8'
    try: content = content_bytes.decode( charset )
    except Exception as exc:
        raise ContentDecodeFailure( url, charset ) from exc
    _scribe.debug( f"Fetched URL: {url}" )
    return Part(
        location = url,
        mimetype = mimetype,
        content = content,
        charset = charset )


# VCS directories to skip during traversal
_VCS_DIRS = frozenset( ( '.git', '.svn', '.hg', '.bzr' ) )
def _collect_directory_files(
    directory: __.Path, recursive: bool
) -> list[ __.Path ]:
    ''' Collects and filters files from directory hierarchy. '''
    import gitignorefile
    cache = gitignorefile.Cache( )
    paths: list[ __.Path ] = [ ]
    for entry in directory.iterdir( ):
        if entry.is_dir( ) and entry.name in _VCS_DIRS:
            _scribe.debug( f"Ignoring VCS directory: {entry}" )
            continue
        path = entry.resolve( )
        path_str = str( path )
        if cache( path_str ):
            _scribe.debug( f"Ignoring path (matched by .gitignore): {entry}" )
            continue
        if entry.is_dir( ) and recursive:
            paths.extend( _collect_directory_files( path, recursive ) )
        elif entry.is_file( ): paths.append( path )
    return paths


def _discover_mimetype( content: bytes, location: str | __.Path ) -> str:
    from magic import from_buffer
    from .exceptions import (
        MimetypeDetermineFailure, TextualMimetypeInvalidity )
    try: mimetype = from_buffer( content, mime = True )
    except Exception as exc:
        raise MimetypeDetermineFailure( location ) from exc
    if not _is_textual_mime( mimetype ):
        raise TextualMimetypeInvalidity( location, mimetype )
    return mimetype


# MIME types that are considered textual beyond those starting with 'text/'
_TEXTUAL_MIME_TYPES = frozenset( (
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/javascript',
    'image/svg+xml',
) )
def _is_textual_mime( mimetype: str ) -> bool:
    ''' Checks if MIME type represents textual content. '''
    _scribe.debug( f"MIME type: {mimetype}" )
    if mimetype.startswith( ( 'text/', 'application/x-', 'text/x-' ) ):
        return True
    return mimetype in _TEXTUAL_MIME_TYPES


def _produce_fs_tasks(
    location: str | __.Path, recursive: bool = False
) -> tuple[ __.cabc.Coroutine[ None, None, Part ], ...]:
    location_ = (
        __.Path( location ) if isinstance( location, str ) else location )
    if location_.is_file( ): return ( _acquire_from_file( location_ ), )
    files = _collect_directory_files( location_, recursive )
    return tuple( _acquire_from_file( f ) for f in files )


def _produce_http_task( url: str ) -> __.cabc.Coroutine[ None, None, Part ]:
    # TODO: URL object rather than string.
    # TODO: Reuse clients for common hosts.

    async def _execute_session( ) -> Part:
        async with __.httpx.AsyncClient( follow_redirects = True ) as client:
            return await _acquire_via_http( client, url )

    return _execute_session( )
