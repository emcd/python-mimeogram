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
from . import parts as _parts


_scribe = __.produce_scribe( __name__ )


def parse( mgtext: str ) -> __.cabc.Sequence[ _parts.Part ]:
    ''' Parses mimeogram. '''
    # TODO? Accept 'strict' flag.
    from .exceptions import MimeogramParseFailure
    if not mgtext.strip( ):
        raise MimeogramParseFailure( reason = "Empty mimeogram." )
    boundary = _extract_boundary( mgtext )
    ptexts = _separate_parts( mgtext, boundary )
    parts: list[ _parts.Part ] = [ ]
    for i, ptext in enumerate( ptexts, 1 ):
        try: part = parse_part( ptext )
        except MimeogramParseFailure:
            _scribe.exception( f"Parse failure on part {i}." )
            continue
        parts.append( part )
        _scribe.debug( f"Parsed part {i} with location '{part.location}'." )
    _scribe.debug( "Parsed {} parts.".format( len( parts ) ) )
    return parts


def parse_part( ptext: str ) -> _parts.Part:
    ''' Parses mimeogram part. '''
    descriptor, content = _parse_descriptor_and_content( ptext )
    _validate_descriptor( descriptor )
    mimetype, charset, linesep = (
        _parse_mimetype( descriptor[ 'Content-Type' ] ) )
    return _parts.Part(
        location = descriptor[ 'Content-Location' ],
        mimetype = mimetype, charset = charset, linesep = linesep,
        content = content )


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
def _parse_descriptor_and_content(
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


_QUOTES = '"\''
def _parse_mimetype( header: str ) -> tuple[ str, str, _parts.LineSeparators ]:
    ''' Extracts MIME type and charset from Content-Type header. '''
    parts = [ p.strip( ) for p in header.split( ';' ) ]
    mimetype = parts[ 0 ]
    charset = 'utf-8'
    linesep = _parts.LineSeparators.LF
    for part in parts[ 1: ]:
        if part.startswith( 'charset=' ):
            charset = part[ 8: ].strip( _QUOTES )
        if part.startswith( 'linesep=' ):
            linesep = _parts.LineSeparators[
                part[ 8: ].strip( _QUOTES ).upper( ) ]
    return mimetype, charset, linesep


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
