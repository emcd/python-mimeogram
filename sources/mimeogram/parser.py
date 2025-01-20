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


''' Parsers for mimeograms and their constituents. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


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


def parse( content: str ) -> __.cabc.Sequence[ Part ]:
    ''' Parses mimeogram. '''
    # TODO? Accept 'strict' flag.
    from .exceptions import MimeogramParseFailure
    if not content.strip( ):
        raise MimeogramParseFailure( reason = "Empty content" )
    boundary = _extract_boundary( content )
    parts_content = _separate_parts( content, boundary )
    if not parts_content:
        raise MimeogramParseFailure( reason = "No parts found" )
    parts: list[ Part ] = [ ]
    for i, part_content in enumerate( parts_content, 1 ):
        headers, content = _parse_descriptor_and_matter( part_content )
        try: _validate_descriptor( headers )
        except MimeogramParseFailure: continue
        content_type, charset = _parse_mimetype( headers[ 'Content-Type' ] )
        parts.append( Part(
            location=headers[ 'Content-Location' ],
            mimetype=content_type,
            charset=charset,
            content=content,
            raw_headers=headers,
            boundary=boundary,
            original_content=part_content ) )
        _scribe.debug(
            "Successfully parsed part {i} with location: {location}".format(
                i = i, location = headers[ 'Content-Location' ] ) )
    _scribe.debug(
        "Successfully parsed {} parts".format( len( parts ) ) )
    return parts


_BOUNDARY_REGEX = __.re.compile(
    r'''^--====MIMEOGRAM_[0-9a-fA-F]{16,}====\s*$''',
    __.re.IGNORECASE | __.re.MULTILINE )
def _extract_boundary( content: str ) -> str:
    ''' Extracts first mimeogram boundary. '''
    mobject = _BOUNDARY_REGEX.search( content )
    if mobject:
        boundary = mobject.group( )
        # Windows clipboard has CRLF newlines. Strip CR before display.
        boundary_s = boundary.rstrip( '\r' )
        _scribe.debug( f"Found boundary: {boundary_s}" )
        # Return with trailing newline to ensure parts are properly split.
        return f"{boundary}\n"
    from .exceptions import MimeogramParseFailure
    raise MimeogramParseFailure( reason = "No mimeogram boundary found." )


_DESCRIPTOR_REGEX = __.re.compile(
    r'''^(?P<name>[\w\-]+)\s*:\s*(?P<value>.*)$''' )
def _parse_descriptor_and_matter(
    content: str
) -> tuple[ __.cabc.Mapping[ str, str ], str ]:
    descriptor: __.cabc.Mapping[ str, str ] = { }
    lines: list[ str ] = [ ]
    in_matter = False
    for line in content.splitlines( ):
        if in_matter:
            lines.append( line )
            continue
        line_s = line.strip( )
        if not line_s:
            in_matter = True
            continue
        mobject = _DESCRIPTOR_REGEX.fullmatch( line_s )
        if not mobject:
            _scribe.warning( "No blank line after headers." )
            in_matter = True
            lines.append( line )
            continue
        name = '-'.join( map(
            str.capitalize, mobject.group( 'name' ).split( '-' ) ) )
        value = mobject.group( 'value' )
        # TODO: Detect duplicates.
        descriptor[ name ] = value
    _scribe.debug( f"Descriptor: {descriptor}" )
    return descriptor, '\n'.join( lines )


def _parse_mimetype( header: str ) -> tuple[ str, str ]:
    ''' Extracts MIME type and charset from Content-Type header. '''
    parts = [ p.strip( ) for p in header.split( ';' ) ]
    mimetype = parts[ 0 ]
    charset = 'utf-8'  # Default charset
    for part in parts[ 1: ]:
        if part.startswith( 'charset=' ):
            charset = part[ 8: ].strip( '"\'' )
    return mimetype, charset


def _separate_parts( content: str, boundary: str ) -> list[ str ]:
    ''' Splits content into parts using boundary. '''
    boundary_s = boundary.rstrip( )
    final_boundary = f"{boundary_s}--"
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
    parts = content_with_parts.split( boundary )[ 1: ]
    _scribe.debug( "Found {} parts to parse.".format( len( parts ) ) )
    return parts


_DESCRIPTOR_INDICES_REQUISITE = frozenset( (
    'Content-Location', 'Content-Type' ) )
def _validate_descriptor(
    descriptor: __.cabc.Mapping[ str, str ]
) -> __.cabc.Mapping[ str, str ]:
    from .exceptions import MimeogramParseFailure
    names = _DESCRIPTOR_INDICES_REQUISITE - descriptor.keys( )
    if names:
        reason = (
            "Missing required headers: {awol}".format(
                awol = ', '.join( names ) ) )
        _scribe.warning( reason )
        raise MimeogramParseFailure( reason = reason )
    return descriptor # TODO: Return immutable.
