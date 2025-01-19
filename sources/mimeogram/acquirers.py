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


# VCS directories to skip during traversal
VCS_DIRS = frozenset( ( '.git', '.svn', '.hg', '.bzr' ) )


# MIME types that are considered textual beyond those starting with 'text/'
TEXTUAL_MIME_TYPES = frozenset( (
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/javascript',
    'image/svg+xml',
) )


def is_textual_mime( mimetype: str ) -> bool:
    ''' Checks if MIME type represents textual content. '''
    _scribe.debug( f"MIME type: {mimetype}" )
    if mimetype.startswith( ( 'text/', 'application/x-', 'text/x-' ) ):
        return True
    return mimetype in TEXTUAL_MIME_TYPES


async def acquire_content_from_file( path: __.Path ) -> Part:
    ''' Acquires content from text file. '''
    # TODO: Factor out MIME check.
    from magic import from_file
    from .exceptions import (
        ContentAcquireFailure,
        MimetypeDetermineFailure,
        TextualMimetypeInvalidity,
    )
    try: mimetype = from_file( path, mime = True )
    except Exception as exc: raise MimetypeDetermineFailure( path ) from exc
    if not is_textual_mime( mimetype ):
        raise TextualMimetypeInvalidity( path, mimetype )
    try:
        async with __.aiofiles.open( path, 'r', encoding = 'utf-8' ) as f:
            content = await f.read( )
    except Exception as exc: raise ContentAcquireFailure( path ) from exc
    _scribe.debug( f"Read file: {path}" )
    return Part(
        location = str( path ), mimetype = mimetype, content = content )


class Acquirer:
    ''' Acquires content from diverse locations. '''

    def __init__( self, strict: bool = False ):
        self.strict = strict
        self.async_client = __.httpx.AsyncClient( follow_redirects = True )

    async def __aenter__( self ):
        return self

    async def __aexit__( self, exc_type, exc_val, exc_tb ):
        await self.async_client.aclose( )

    async def acquire(
        self,
        sources: __.cabc.Sequence[ str | __.Path ],
        recursive: bool = False
    ) -> __.cabc.Sequence[ Part ]:
        ''' Acquires content from multiple sources. '''
        from asyncio import create_task, gather
        from urllib.parse import urlparse
        tasks = [ ]
        for source in sources:
            url_parts = (
                urlparse( source ) if isinstance( source, str )
                else urlparse( str( source ) ) )
            match url_parts.scheme:
                case 'http' | 'https':
                    tasks.append( create_task(
                        _acquire_via_http(
                            self.async_client, source ) ) )
                case '' | 'file':
                    path = (
                        __.Path( source )
                        if isinstance( source, str ) else source )
                    if path.is_dir():
                        paths = _collect_directory_files( path, recursive )
                        tasks.extend(
                            create_task( acquire_content_from_file( p ) )
                            for p in paths )
                    else:
                        tasks.append( create_task(
                            acquire_content_from_file( path ) ) )
                case _:
                    pass # TODO: Raise exception for unsupported URL scheme.
        results = await gather( *tasks, return_exceptions = True )
        valid_parts = [ ]
        for item in results:
            if isinstance( item, Exception ):
                if self.strict: raise item
                _scribe.error( f"Error processing source: {item}" )
            elif item is not None: valid_parts.append( item )
        return valid_parts


async def _acquire_via_http(
    client: __.httpx.AsyncClient, url: str
) -> Part:
    ''' Acquires content via HTTP/HTTPS. '''
    # TODO: Factor out MIME check.
    from magic import from_buffer
    from .exceptions import (
        ContentAcquireFailure,
        ContentDecodeFailure,
        MimetypeDetermineFailure,
        TextualMimetypeInvalidity,
    )
    try:
        response = await client.get( url )
        response.raise_for_status( )
    except Exception as exc: raise ContentAcquireFailure( url ) from exc
    mimetype = (
        response.headers.get( 'content-type', 'application/octet-stream' )
        .split( ';' )[ 0 ].strip( ) )
    content_bytes = response.content
    if not is_textual_mime( mimetype ):
        try: mimetype = from_buffer( content_bytes, mime = True )
        except Exception as exc:
            raise MimetypeDetermineFailure( url ) from exc
    if not is_textual_mime( mimetype ):
        raise TextualMimetypeInvalidity( url, mimetype )
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


def _collect_directory_files(
    directory: __.Path, recursive: bool
) -> list[ __.Path ]:
    ''' Collects and filters files from directory hierarchy. '''
    import gitignorefile
    cache = gitignorefile.Cache( )
    paths = [ ]
    for entry in directory.iterdir( ):
        if entry.is_dir( ) and entry.name in VCS_DIRS:
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
