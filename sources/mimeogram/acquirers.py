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
    auxdata: __.Globals, sources: __.cabc.Sequence[ str | __.Path ]
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
    if strict: return await __.gather_async( *tasks )
    results = await __.gather_async( *tasks, return_exceptions = True )
    # TODO: Factor into '__.generics.extract_results_filter_errors'.
    values: list[ _parts.Part ] = [ ]
    for result in results:
        if result.is_error( ):
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
    mimetype, charset = _detect_mimetype_and_charset( content_bytes, location )
    if charset is None: raise ContentDecodeFailure( location, '???' )
    linesep = _parts.LineSeparators.detect_bytes( content_bytes )
    if linesep is None:
        _scribe.warning( f"No line separator detected in '{location}'." )
        linesep = _parts.LineSeparators( __.os.linesep )
    try: content = content_bytes.decode( charset )
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
    mimetype = (
        response.headers.get( 'content-type', 'application/octet-stream' )
        .split( ';' )[ 0 ].strip( ) )
    content_bytes = response.content
    charset = response.encoding or _detect_charset( content_bytes )
    if charset is None: raise ContentDecodeFailure( url, '???' )
    if not _is_textual_mimetype( mimetype ):
        mimetype, _ = (
            _detect_mimetype_and_charset(
                content_bytes, url, charset = charset ) )
    linesep = _parts.LineSeparators.detect_bytes( content_bytes )
    if linesep is None:
        _scribe.warning( f"No line separator detected in '{url}'." )
        linesep = _parts.LineSeparators( __.os.linesep )
    try: content = content_bytes.decode( charset )
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


def _detect_charset( content: bytes ) -> str | None:
    from chardet import detect
    charset = detect( content )[ 'encoding' ]
    if charset is None: return charset
    if charset.startswith( 'utf' ): return charset
    match charset:
        case 'ascii': return 'utf-8' # Assume superset.
        case _: pass
    # Shake out false positives, like 'MacRoman'.
    try: content.decode( 'utf-8' )
    except UnicodeDecodeError: return charset
    return 'utf-8'


def _detect_mimetype( content: bytes, location: str | __.Path ) -> str | None:
    from mimetypes import guess_type
    from puremagic import PureError, from_string # pyright: ignore
    try: return from_string( content, mime = True )
    except ( PureError, ValueError ):
        return guess_type( str( location ) )[ 0 ]


def _detect_mimetype_and_charset(
    content: bytes,
    location: str | __.Path, *,
    mimetype: __.Absential[ str ] = __.absent,
    charset: __.Absential[ str ] = __.absent,
) -> tuple[ str, str | None ]:
    from .exceptions import TextualMimetypeInvalidity
    if __.is_absent( mimetype ):
        mimetype_ = _detect_mimetype( content, location )
    else: mimetype_ = mimetype
    if __.is_absent( charset ): # noqa: SIM108
        charset_ = _detect_charset( content )
    else: charset_ = charset
    if not mimetype_:
        if charset_:
            mimetype_ = 'text/plain'
            _validate_mimetype_with_trial_decode(
                content, location, mimetype_, charset_ )
            return mimetype_, charset_
        mimetype_ = 'application/octet-stream'
    if _is_textual_mimetype( mimetype_ ):
        return mimetype_, charset_
    if charset_ is None:
        raise TextualMimetypeInvalidity( location, mimetype_ )
    _validate_mimetype_with_trial_decode(
        content, location, mimetype_, charset_ )
    return mimetype_, charset_


def _is_reasonable_text_content( content: str ) -> bool:
    ''' Checks if decoded content appears to be meaningful text. '''
    if not content: return False
    # Check for excessive repetition of single characters (likely binary)
    if len( set( content ) ) == 1: return False
    # Check for excessive control characters (excluding common whitespace)
    common_whitespace = '\t\n\r'
    ascii_control_limit = 32
    control_chars = sum(
        1 for c in content
        if ord( c ) < ascii_control_limit and c not in common_whitespace )
    if control_chars > len( content ) * 0.1: return False  # >10% control chars
    # Check for reasonable printable character ratio
    printable_chars = sum(
        1 for c in content if c.isprintable( ) or c in common_whitespace )
    return printable_chars >= len( content ) * 0.8  # >=80% printable


# MIME types that are considered textual beyond those starting with 'text/'.
_TEXTUAL_MIME_TYPES = frozenset( (
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/x-perl',
    'application/x-python',
    'application/x-php',
    'application/x-ruby',
    'application/x-shell',
    'application/javascript',
    'image/svg+xml',
) )
# MIME type suffixes that indicate textual content.
_TEXTUAL_SUFFIXES = ( '+xml', '+json', '+yaml', '+toml' )
def _is_textual_mimetype( mimetype: str ) -> bool:
    ''' Checks if MIME type represents textual content. '''
    _scribe.debug( f"MIME type: {mimetype}" )
    if mimetype.startswith( ( 'text/', 'text/x-' ) ): return True
    if mimetype in _TEXTUAL_MIME_TYPES: return True
    if mimetype.endswith( _TEXTUAL_SUFFIXES ):
        _scribe.debug(
            f"MIME type '{mimetype}' accepted due to textual suffix." )
        return True
    return False


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


def _validate_mimetype_with_trial_decode(
    content: bytes, location: str | __.Path, mimetype: str, charset: str
) -> None:
    ''' Validates charset fallback and returns appropriate MIME type. '''
    from .exceptions import TextualMimetypeInvalidity
    try: text = content.decode( charset )
    except ( UnicodeDecodeError, LookupError ) as exc:
        raise TextualMimetypeInvalidity( location, mimetype ) from exc
    if _is_reasonable_text_content( text ):
        _scribe.debug(
            f"MIME type '{mimetype}' accepted after successful "
            f"decode test with charset '{charset}' for '{location}'." )
        return
    raise TextualMimetypeInvalidity( location, mimetype )
