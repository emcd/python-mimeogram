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

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from . import __
from .exceptions import MimeogramError


logger = logging.getLogger(__name__)


# VCS directories to skip during traversal
VCS_DIRS = frozenset(('.git', '.svn', '.hg', '.bzr'))


# MIME types that are considered textual beyond those starting with 'text/'
TEXTUAL_MIME_TYPES = frozenset((
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/javascript',
    'image/svg+xml',
    'text/x-python',
    'text/x-script.python',
))


@dataclass
class Part:
    ''' A part of a mimeogram bundle. '''
    location: str
    content_type: str
    content: str
    charset: str = 'utf-8'


def is_textual_mime(mime_type: str) -> bool:
    ''' Check if a MIME type represents textual content. '''
    if mime_type.startswith(('text/', 'application/x-', 'text/x-')):
        return True
    return mime_type in TEXTUAL_MIME_TYPES


class ContentFetcher:
    ''' Handles content acquisition from various sources. '''

    def __init__(self, strict: bool = False):
        self.strict = strict
        # Import here to avoid module-level dependencies
        import httpx
        import magic
        self.magic = magic.Magic(mime=True)
        self.async_client = httpx.AsyncClient(follow_redirects=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_client.aclose()

    async def _read_file(self, path: Path) -> __.typx.Optional[Part]:
        try:
            mime_type = self.magic.from_file(str(path))
            if not is_textual_mime(mime_type):
                if self.strict:
                    raise MimeogramError(f'Non-textual file: {path} ({mime_type})')
                logger.debug('Skipping non-textual file: %s (%s)', path, mime_type)
                return None

            # Import here to avoid module-level dependency
            import aiofiles
            async with aiofiles.open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = await f.read()

            logger.debug('Read file: %s', path)
            return Part(
                location=str(path),
                content_type=mime_type,
                content=content
            )
        except Exception as e:
            if self.strict:
                raise MimeogramError(f'Failed to read file {path}') from e
            logger.warning('Failed to read file %s: %s', path, str(e))
            return None

    async def _fetch_url(self, url: str) -> __.typx.Optional[Part]:
        try:
            response = await self.async_client.get(url)
            response.raise_for_status()

            mime_type = response.headers.get('content-type', 'application/octet-stream').split(';')[0].strip()
            content_bytes = response.content

            if not is_textual_mime(mime_type):
                detected = self.magic.from_buffer(content_bytes)
                if not is_textual_mime(detected):
                    if self.strict:
                        raise MimeogramError(
                            f'Non-textual content at {url} '
                            f'(reported: {mime_type}, detected: {detected})'
                        )
                    logger.debug('Skipping non-textual URL content: %s', url)
                    return None
                mime_type = detected

            encoding = response.encoding or 'utf-8'
            content = content_bytes.decode(encoding, errors='replace')

            logger.debug('Fetched URL: %s', url)
            return Part(
                location=url,
                content_type=mime_type,
                content=content,
                charset=encoding
            )
        except Exception as e:
            if self.strict:
                raise MimeogramError(f'Failed to fetch URL {url}') from e
            logger.warning('Failed to fetch URL %s: %s', url, str(e))
            return None

    def _gather_files_in_directory(
        self, directory: Path, cache: __.cabc.Callable, recursive: bool
    ) -> __.cabc.Sequence[asyncio.Task]:
        tasks = []
        for entry in directory.iterdir():
            # Skip VCS directories
            if entry.is_dir() and entry.name in VCS_DIRS:
                logger.debug('Ignoring VCS directory: %s', entry)
                continue

            path_str = str(entry.resolve())
            if cache(path_str):
                logger.debug('Ignoring path (matched by .gitignore): %s', entry)
                continue

            if entry.is_dir() and recursive:
                tasks.extend(self._gather_files_in_directory(entry, cache, recursive))
            elif entry.is_file():
                tasks.append(asyncio.create_task(self._read_file(entry)))

        return tasks

    async def fetch_sources(
        self, sources: __.cabc.Sequence[str | Path], recursive: bool = False
    ) -> __.cabc.Sequence[Part]:
        tasks = []

        for source in sources:
            if isinstance(source, str) and urlparse(source).scheme in ('http', 'https'):
                tasks.append(asyncio.create_task(self._fetch_url(source)))
            else:
                path = Path(source) if isinstance(source, str) else source
                if path.is_dir():
                    # Import here to avoid module-level dependency
                    import gitignorefile
                    cache = gitignorefile.Cache()
                    tasks.extend(self._gather_files_in_directory(path, cache, recursive))
                else:
                    tasks.append(asyncio.create_task(self._read_file(path)))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_parts = []
        for item in results:
            if isinstance(item, Exception):
                if self.strict:
                    raise item
                logger.error('Error processing source: %s', str(item))
            elif item is not None:
                valid_parts.append(item)
        return valid_parts
