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

import magic as _magic

from . import __


_scribe = __.produce_scribe(__name__)


@__.dataclass
class Part:
    """A part of a mimeogram bundle."""
    location: str
    content_type: str
    content: str
    charset: str = 'utf-8'


# VCS directories to skip during traversal
VCS_DIRS = frozenset(('.git', '.svn', '.hg', '.bzr'))


# MIME types that are considered textual beyond those starting with 'text/'
TEXTUAL_MIME_TYPES = frozenset((
    'application/json',
    'application/xml',
    'application/xhtml+xml',
    'application/javascript',
    'image/svg+xml',
))


def is_textual_mime(mime_type: str) -> bool:
    """Check if a MIME type represents textual content."""
    _scribe.debug( f"MIME type: {mime_type}" )
    if mime_type.startswith(('text/', 'application/x-', 'text/x-')):
        return True
    return mime_type in TEXTUAL_MIME_TYPES


async def read_text_file(path: __.Path, strict: bool) -> __.typx.Optional[Part]:
    """Read content from a text file."""
    from .exceptions import ContentReadFailure
    try:
        mime_type = _magic.from_file( str( path ), mime = True)
        if not is_textual_mime(mime_type):
            if strict:
                raise ContentReadFailure(f'Non-textual file: {path} ({mime_type})')
            _scribe.debug('Skipping non-textual file: %s (%s)', path, mime_type)
            return None
        async with __.aiofiles.open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = await f.read()
        _scribe.debug('Read file: %s', path)
        return Part(
            location=str(path), content_type=mime_type, content=content )
    except ContentReadFailure: raise
    except Exception as exc:
        if strict:
            raise ContentReadFailure(f'Failed to read file {path}') from exc
        _scribe.warning('Failed to read file %s: %s', path, str(exc))
        return


async def fetch_url_content(
    client: __.httpx.AsyncClient,
    url: str,
    strict: bool
) -> __.typx.Optional[Part]:
    """Fetch content from URL."""
    from .exceptions import ContentFetchFailure

    # Fetch content
    try:
        response = await client.get(url)
        response.raise_for_status()
    except Exception as exc:
        if strict:
            raise ContentFetchFailure(f'Failed to fetch {url}') from exc
        _scribe.warning('Failed to fetch %s: %s', url, str(exc))
        return None

    # Get MIME type from headers
    mime_type = (
        response.headers.get('content-type', 'application/octet-stream')
        .split(';')[0]
        .strip()
    )
    content_bytes = response.content

    # Check content type
    if not is_textual_mime(mime_type):
        try: detected = _magic.from_buffer( content_bytes, mime = True )
        except Exception as exc:
            if strict:
                raise ContentFetchFailure(
                    f'Failed to detect MIME type for {url}'
                ) from exc
            _scribe.warning(
                'Failed to detect MIME type for %s: %s',
                url, str(exc)
            )
            return None

        if not is_textual_mime(detected):
            if strict:
                raise ContentFetchFailure(
                    f'Non-textual content at {url} '
                    f'(reported: {mime_type}, detected: {detected})'
                )
            _scribe.debug('Skipping non-textual URL content: %s', url)
            return None
        mime_type = detected

    # Decode content
    try:
        encoding = response.encoding or 'utf-8'
        content = content_bytes.decode(encoding, errors='replace')
    except Exception as exc:
        if strict:
            raise ContentFetchFailure(
                f'Failed to decode content from {url}'
            ) from exc
        _scribe.warning(
            'Failed to decode content from %s: %s',
            url, str(exc)
        )
        return None

    _scribe.debug('Fetched URL: %s', url)
    return Part(
        location=url,
        content_type=mime_type,
        content=content,
        charset=encoding
    )


def gather_files_in_directory(
    directory: __.Path,
    cache: __.cabc.Callable,
    recursive: bool
) -> list[__.Path]:
    """Gather file paths from directory."""
    paths = []

    for entry in directory.iterdir():
        # Skip VCS directories
        if entry.is_dir() and entry.name in VCS_DIRS:
            _scribe.debug('Ignoring VCS directory: %s', entry)
            continue

        path = entry.resolve()
        path_str = str(path)

        if cache(path_str):
            _scribe.debug('Ignoring path (matched by .gitignore): %s', entry)
            continue

        if entry.is_dir() and recursive:
            paths.extend(gather_files_in_directory(path, cache, recursive))
        elif entry.is_file():
            paths.append(path)

    return paths


class ContentFetcher:
    """Fetch content from files and URLs."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.async_client = __.httpx.AsyncClient(follow_redirects=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_client.aclose()

    async def fetch_sources(
        self,
        sources: __.cabc.Sequence[str | __.Path],
        recursive: bool = False
    ) -> __.cabc.Sequence[Part]:
        """Fetch content from multiple sources."""
        from urllib.parse import urlparse
        tasks = []
        for source in sources:
            if isinstance(source, str) and urlparse(source).scheme in ('http', 'https'):
                tasks.append(
                    __.asyncio.create_task(
                        fetch_url_content(self.async_client, source, self.strict)
                    )
                )
            else:
                _scribe.debug( f"Fetching source: {source}" )
                path = __.Path(source) if isinstance(source, str) else source
                if path.is_dir():
                    import gitignorefile
                    cache = gitignorefile.Cache()
                    paths = gather_files_in_directory(path, cache, recursive)
                    tasks.extend(
                        __.asyncio.create_task(read_text_file(p, self.strict))
                        for p in paths
                    )
                else:
                    tasks.append(
                        __.asyncio.create_task(read_text_file(path, self.strict))
                    )
        results = await __.asyncio.gather(*tasks, return_exceptions=True)
        valid_parts = []
        for item in results:
            if isinstance(item, Exception):
                if self.strict:
                    raise item
                _scribe.error('Error processing source: %s', str(item))
            elif item is not None:
                valid_parts.append(item)
        return valid_parts
