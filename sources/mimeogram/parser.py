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


_scribe = __.produce_scribe(__name__)


REQUIRED_HEADERS = frozenset(('Content-Location', 'Content-Type'))
BOUNDARY_PATTERN = r'^--====MIMEOGRAM_[0-9a-fA-F]{16,}====(?:--)?\s*$'


@__.dataclass
class ParsedPart:
    """A parsed part from a mimeogram bundle."""
    location: str
    content_type: str
    charset: str
    content: str
    raw_headers: __.cabc.Mapping[str, str]
    boundary: str
    original_content: __.typx.Optional[str] = None


def parse_content_type(header: str) -> tuple[str, str]:
    """Extract content type and charset from Content-Type header."""
    parts = [p.strip() for p in header.split(';')]
    content_type = parts[0]
    charset = 'utf-8'  # Default charset

    for part in parts[1:]:
        if part.startswith('charset='):
            charset = part[8:].strip('"\'')

    return content_type, charset


def parse_headers(content: str) -> tuple[__.cabc.Mapping[str, str], str]:
    """Parse headers and content from a part."""
    from .exceptions import ContentParsingFailure

    # Split headers and content
    try:
        headers_text, content = content.split('\n\n', 1)
    except ValueError:
        # No blank line - try to parse anyway
        _scribe.warning('No blank line after headers')
        for i, line in enumerate(content.splitlines()):
            if ':' not in line:
                headers_text = '\n'.join(content.splitlines()[:i])
                content = '\n'.join(content.splitlines()[i:])
                break
        else:
            raise ContentParsingFailure('Could not find end of headers')

    # Parse individual headers
    headers = {}
    for line in headers_text.splitlines():
        if ':' not in line:
            _scribe.warning('Malformed header line: %s', line)
            continue

        key, value = line.split(':', 1)
        headers[key.strip()] = value.strip()

    # Check required headers
    missing = REQUIRED_HEADERS - headers.keys()
    if missing:
        raise ContentParsingFailure(f'Missing required headers: {missing}')

    return headers, content.strip()


def extract_boundary(content: str) -> __.typx.Optional[str]:
    """Find first mimeogram boundary in content."""
    import re

    boundary_pattern = re.compile(BOUNDARY_PATTERN, re.MULTILINE | re.IGNORECASE)
    match = boundary_pattern.search(content)

    if match:
        return match.group().lstrip('-')  # Strip leading dashes
    return None


def split_parts(content: str, boundary: str) -> list[str]:
    """Split content into parts using boundary."""
    final_boundary = f'--{boundary}--'
    regular_boundary = f'--{boundary}'

    # Try to split on final boundary first
    final_parts = content.split(final_boundary)
    if len(final_parts) > 1:
        _scribe.debug('Found final boundary')
        content_with_parts = final_parts[0]
        trailing_text = final_parts[1]
        if trailing_text.strip():
            _scribe.debug('Found trailing text: %s', trailing_text.strip())
    else:
        _scribe.warning('No final boundary found')
        content_with_parts = content

    # Split remaining content on regular boundary
    parts = content_with_parts.split(regular_boundary)[1:]  # Skip pre-boundary text
    _scribe.debug('Found %d parts to parse', len(parts))

    return parts


def parse_bundle(content: str) -> __.cabc.Sequence[ParsedPart]:
    """Parse a mimeogram bundle into parts."""
    from .exceptions import ContentParsingFailure

    if not content.strip():
        raise ContentParsingFailure('Empty content')

    # Find first boundary
    boundary = extract_boundary(content)
    if not boundary:
        raise ContentParsingFailure('No mimeogram boundary found')

    _scribe.debug('Found boundary: %s', boundary)

    # Split into parts
    parts_content = split_parts(content, boundary)
    if not parts_content:
        raise ContentParsingFailure('No parts found')

    # Parse each part
    parsed_parts = []
    for i, part_content in enumerate(parts_content, 1):
        headers, content = parse_headers(part_content.strip())
        content_type, charset = parse_content_type(headers['Content-Type'])

        parsed_parts.append(ParsedPart(
            location=headers['Content-Location'],
            content_type=content_type,
            charset=charset,
            content=content,
            raw_headers=headers,
            boundary=boundary,
            original_content=part_content
        ))
        _scribe.debug(
            'Successfully parsed part %d with location: %s',
            i, headers['Content-Location']
        )

    _scribe.debug('Successfully parsed %d parts', len(parsed_parts))
    return parsed_parts
