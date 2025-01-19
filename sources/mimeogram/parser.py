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


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


REQUIRED_HEADERS = frozenset( ( 'Content-Location', 'Content-Type' ) )
BOUNDARY_PATTERN = r'^--====MIMEOGRAM_[0-9a-fA-F]{16,}====(?:--)?\s*$'


@__.dataclass
class Part:
    ''' Part parsed from mimeogram. '''
    location: str
    mimetype: str
    charset: str
    content: str
    raw_headers: __.cabc.Mapping[ str, str ]
    boundary: str
    original_content: __.typx.Optional[ str ] = None


def parse_mimetype( header: str ) -> tuple[ str, str ]:
    ''' Extracts MIME type and charset from Content-Type header. '''
    parts = [ p.strip() for p in header.split( ';' ) ]
    mimetype = parts[ 0 ]
    charset = 'utf-8'  # Default charset
    for part in parts[ 1: ]:
        if part.startswith( 'charset=' ):
            charset = part[ 8: ].strip( '"\'' )
    return mimetype, charset


def parse_headers( content: str ) -> tuple[ __.cabc.Mapping[ str, str ], str ]:
    ''' Parses headers and content from a part. '''
    from .exceptions import MimeogramParseFailure
    # TODO: Rewrite to use a single pass.
    # TODO? Use 'split' instead of 'splitlines'.
    # Split headers and content
    try: headers_text, content = content.split( '\n\n', 1 )
    except ValueError as exc:
        # No blank line - try to parse anyway
        _scribe.warning( "No blank line after headers" )
        for i, line in enumerate( content.splitlines( ) ):
            if ':' not in line:
                headers_text = '\n'.join( content.splitlines( )[ :i ] )
                content = '\n'.join( content.splitlines( )[ i: ] )
                break
        else:
            raise MimeogramParseFailure(
                reason = "Could not find end of headers" ) from exc
    # Parse individual headers
    headers = { }
    for line in headers_text.splitlines( ):
        if ':' not in line:
            _scribe.warning( "Malformed header line: %s", line )
            continue
        key, value = line.split( ':', 1 )
        headers[ key.strip( ) ] = value.strip( )
    # Check required headers
    missing = REQUIRED_HEADERS - headers.keys( )
    if missing:
        raise MimeogramParseFailure(
            reason = f"Missing required headers: {missing}" )
    return headers, content.strip( )


def extract_boundary( content: str ) -> str:
    ''' Finds first mimeogram boundary in content. '''
    import re
    boundary_pattern = (
        re.compile( BOUNDARY_PATTERN, re.MULTILINE | re.IGNORECASE ) )
    match = boundary_pattern.search( content )
    if match:
        # Windows clipboard has CRLF newlines.
        # Need to strip carriage returns and other whitespace from end.
        boundary = match.group( ).rstrip( ).lstrip( '-' )
        _scribe.debug( 'Found boundary: %s', boundary )
        return boundary
    from .exceptions import MimeogramParseFailure
    raise MimeogramParseFailure( reason = "No mimeogram boundary found." )


def split_parts( content: str, boundary: str ) -> list[ str ]:
    ''' Splits content into parts using boundary. '''
    regular_boundary = f"--{boundary}"
    final_boundary = f"{regular_boundary}--"
    # Detect final boundary and trailing text first.
    final_parts = content.split( final_boundary )
    if len( final_parts ) > 1:
        _scribe.debug( "Found final boundary." )
        content_with_parts = final_parts[ 0 ]
        trailing_text = final_parts[ 1 ].strip( )
        if trailing_text: _scribe.debug( "Found trailing text." )
    else:
        _scribe.warning( "No final boundary found." )
        content_with_parts = content
    # Split remaining content on regular boundary and skip leading text.
    parts = content_with_parts.split( regular_boundary )[ 1: ]
    _scribe.debug( "Found %d parts to parse.", len( parts ) )
    return parts


def parse( content: str ) -> __.cabc.Sequence[ Part ]:
    ''' Parses mimeogram. '''
    from .exceptions import MimeogramParseFailure
    if not content.strip( ):
        raise MimeogramParseFailure( reason = "Empty content" )
    boundary = extract_boundary( content )
    parts_content = split_parts( content, boundary )
    if not parts_content:
        raise MimeogramParseFailure( reason = "No parts found" )
    parsed_parts = [ ]
    for i, part_content in enumerate( parts_content, 1 ):
        headers, content = parse_headers( part_content.strip( ) )
        content_type, charset = parse_mimetype( headers[ 'Content-Type' ] )
        parsed_parts.append( Part(
            location=headers[ 'Content-Location' ],
            mimetype=content_type,
            charset=charset,
            content=content,
            raw_headers=headers,
            boundary=boundary,
            original_content=part_content ) )
        _scribe.debug(
            "Successfully parsed part %d with location: %s",
            i, headers[ 'Content-Location' ] )
    _scribe.debug( "Successfully parsed %d parts", len( parsed_parts ) )
    return parsed_parts
