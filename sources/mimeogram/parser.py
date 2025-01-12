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

from dataclasses import dataclass

from . import __


@dataclass
class ParsedPart:
    """A parsed part from a mimeogram bundle."""
    location: str
    content_type: str
    charset: str
    content: str
    raw_headers: __.cabc.Mapping[str, str]
    boundary: str
    original_content: __.typx.Optional[str] = None


class ParserError(Exception):
    """Base class for parser-specific errors."""


class Parser:
    """Parse mimeogram bundles into parts."""

    # Headers we require
    REQUIRED_HEADERS = frozenset(('Content-Location', 'Content-Type'))

    # Boundary pattern for part splitting
    BOUNDARY_PATTERN = r'^--====MIMEOGRAM_[0-9a-fA-F]{16,}====(?:--)?\s*$'

    @staticmethod
    def _parse_headers(content: str) -> tuple[__.cabc.Mapping[str, str], str]:
        """Parse headers and content from a part's content.

        Args:
            content: The part's content including headers

        Returns:
            Tuple of (headers dict, remaining content)

        Raises:
            ParserError: If required headers are missing
        """
        import logging
        logger = logging.getLogger(__name__)

        # Split headers and content
        try:
            headers_text, content = content.split('\n\n', 1)
        except ValueError:
            # No blank line - try to parse anyway
            logger.warning('No blank line after headers')
            for i, line in enumerate(content.splitlines()):
                if ':' not in line:
                    headers_text = '\n'.join(content.splitlines()[:i])
                    content = '\n'.join(content.splitlines()[i:])
                    break
            else:
                raise ParserError('Could not find end of headers')

        # Parse individual headers
        headers = {}
        for line in headers_text.splitlines():
            if ':' not in line:
                logger.warning('Malformed header line: %s', line)
                continue

            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()

        # Check required headers
        missing = Parser.REQUIRED_HEADERS - headers.keys()
        if missing:
            raise ParserError(f'Missing required headers: {missing}')

        return headers, content.strip()

    @staticmethod
    def _parse_content_type(header: str) -> tuple[str, str]:
        """Parse Content-Type header into type and charset.

        Returns:
            Tuple of (content_type, charset)
        """
        parts = [p.strip() for p in header.split(';')]
        content_type = parts[0]
        charset = 'utf-8'  # Default charset

        for part in parts[1:]:
            if part.startswith('charset='):
                charset = part[8:].strip('"\'')

        return content_type, charset

    @staticmethod
    def parse(content: str) -> __.cabc.Sequence[ParsedPart]:
        """Parse a mimeogram bundle into its constituent parts.

        Args:
            content: The complete mimeogram bundle text

        Returns:
            Sequence of parsed parts

        Raises:
            ParserError: If content cannot be parsed
        """
        import re
        import logging
        logger = logging.getLogger(__name__)

        if not content.strip():
            raise ParserError('Empty content')

        # Find first boundary
        boundary_pattern = re.compile(Parser.BOUNDARY_PATTERN, re.MULTILINE | re.IGNORECASE)
        match = boundary_pattern.search(content)
        if not match:
            raise ParserError('No mimeogram boundary found')

        boundary_text = match.group()  # Complete boundary text with '--' prefix
        logger.debug('Found boundary: %s', boundary_text)

        # Try to split on final boundary first
        final_parts = content.split(boundary_text + '--')
        if len(final_parts) > 1:
            logger.debug('Found final boundary')
            content_with_parts = final_parts[0]
            trailing_text = final_parts[1]
            if trailing_text.strip():
                logger.debug('Found trailing text: %s', trailing_text.strip())
        else:
            logger.warning('No final boundary found')
            content_with_parts = content

        # Split remaining content on regular boundary
        parts_content = content_with_parts.split(boundary_text)[1:]  # Skip pre-boundary text
        logger.debug('Found %d parts to parse', len(parts_content))

        if not parts_content:
            raise ParserError('No parts found')

        # Parse each part
        parsed_parts = []
        for i, part_content in enumerate(parts_content):
            try:
                logger.debug('Parsing part %d (%d bytes)', i + 1, len(part_content))
                headers, content = Parser._parse_headers(part_content.strip())
                logger.debug('Part %d headers: %s', i + 1, headers)
                content_type, charset = Parser._parse_content_type(headers['Content-Type'])

                parsed_parts.append(ParsedPart(
                    location=headers['Content-Location'],
                    content_type=content_type,
                    charset=charset,
                    content=content,
                    raw_headers=headers,
                    boundary=boundary_text.lstrip('-'),
                    original_content=part_content
                ))
                logger.debug('Successfully parsed part %d with location: %s', i + 1, headers['Content-Location'])
            except Exception as e:
                raise ParserError(f'Failed to parse part {i + 1}: {str(e)}') from e

        logger.debug('Successfully parsed %d parts', len(parsed_parts))
        return parsed_parts
