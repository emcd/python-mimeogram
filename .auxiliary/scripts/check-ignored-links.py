#!/usr/bin/env python3
# vim: set filetype=python fileencoding=utf-8:

''' Verifies URLs excluded from Sphinx linkcheck via ``linkcheck_ignore``. '''

from __future__ import annotations

import argparse
import ast
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from urllib.parse import urlsplit


URL_PATTERN = re.compile( r'https?://[^\s<>()\'"`]+' )
HTTP_STATUS_REDIRECT_MIN = 300
HTTP_STATUS_BAD_REQUEST = 400
STATUS_METHOD_NOT_ALLOWED = 405
STATUS_NOT_IMPLEMENTED = 501
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
VALID_SCHEMES = frozenset( { 'http', 'https' } )


@dataclass( frozen = True )
class CheckResult:
    ''' Stores URL check result metadata. '''

    url: str
    status: int | None
    final_url: str | None
    note: str
    ok: bool


def _iter_documentation_files( root: Path ) -> Sequence[ Path ]:
    files = [ root / 'README.rst' ]
    documentation = root / 'documentation'
    for extension in ( '*.rst', '*.md' ):
        files.extend( sorted( documentation.rglob( extension ) ) )
    return tuple( file for file in files if file.is_file( ) )


def _extract_urls_from_files( files: Sequence[ Path ] ) -> tuple[ str, ... ]:
    urls: list[ str ] = [ ]
    seen: set[ str ] = set( )
    for file in files:
        text = file.read_text( encoding = 'utf-8' )
        for match in URL_PATTERN.findall( text ):
            # Drop punctuation that commonly follows URLs in prose.
            url = match.rstrip( '.,;:!?)' )
            if url in seen: continue
            seen.add( url )
            urls.append( url )
    return tuple( urls )


def _load_linkcheck_ignore_patterns( conf_path: Path ) -> tuple[ str, ... ]:
    source = conf_path.read_text( encoding = 'utf-8' )
    module = ast.parse( source, filename = str( conf_path ) )
    for node in module.body:
        if not isinstance( node, ast.Assign ): continue
        for target in node.targets:
            if not isinstance( target, ast.Name ): continue
            if target.id != 'linkcheck_ignore': continue
            value = ast.literal_eval( node.value )
            if not isinstance( value, list ):
                raise TypeError
            return tuple( str( item ) for item in value )
    raise LookupError


def _assert_http_scheme( url: str ) -> None:
    scheme = urlsplit( url ).scheme
    if scheme in VALID_SCHEMES: return
    raise ValueError


def _filter_ignored_urls(
    urls: Sequence[ str ],
    ignore_patterns: Sequence[ str ],
) -> tuple[ str, ... ]:
    regexes = tuple( re.compile( pattern ) for pattern in ignore_patterns )
    return tuple(
        url for url in urls
        if any( regex.search( url ) for regex in regexes )
    )


def _request_url(
    url: str,
    timeout: float,
    user_agent: str,
    method: str,
) -> CheckResult:
    _assert_http_scheme( url )
    request = urllib.request.Request(  # noqa: S310
        url,
        headers = { 'User-Agent': user_agent },
        method = method,
    )
    try:
        with urllib.request.urlopen( request, timeout = timeout ) as response: # noqa: S310
            status = response.getcode( )
            final_url = response.geturl( )
            return CheckResult(
                url = url,
                status = status,
                final_url = final_url,
                note = method,
                ok = status < HTTP_STATUS_BAD_REQUEST,
            )
    except urllib.error.HTTPError as exc:
        return CheckResult(
            url = url,
            status = exc.code,
            final_url = str( exc.geturl( ) ),
            note = f'{method} HTTPError',
            ok = False,
        )
    except urllib.error.URLError as exc:
        return CheckResult(
            url = url,
            status = None,
            final_url = None,
            note = f'{method} URLError: {exc.reason}',
            ok = False,
        )


def _normalize_result(
    result: CheckResult,
    strict_access: bool,
) -> CheckResult:
    if result.ok: return result
    if result.status is None: return result
    if HTTP_STATUS_REDIRECT_MIN <= result.status < HTTP_STATUS_BAD_REQUEST:
        return CheckResult(
            url = result.url,
            status = result.status,
            final_url = result.final_url,
            note = f'{result.note} (treated as reachable redirect)',
            ok = True,
        )
    if result.status not in ( STATUS_UNAUTHORIZED, STATUS_FORBIDDEN ):
        return result
    if strict_access: return result
    return CheckResult(
        url = result.url,
        status = result.status,
        final_url = result.final_url,
        note = f'{result.note} (treated as reachable)',
        ok = True,
    )


def _check_url(
    url: str,
    timeout: float,
    user_agent: str,
    strict_access: bool,
) -> CheckResult:
    result = _normalize_result( _request_url(
        url = url,
        timeout = timeout,
        user_agent = user_agent,
        method = 'HEAD',
    ), strict_access = strict_access )
    if result.ok: return result
    if result.status not in (
        STATUS_METHOD_NOT_ALLOWED,
        STATUS_NOT_IMPLEMENTED,
    ):
        return result
    return _normalize_result( _request_url(
        url = url,
        timeout = timeout,
        user_agent = user_agent,
        method = 'GET',
    ), strict_access = strict_access )


def main( ) -> int:
    parser = argparse.ArgumentParser(
        description = (
            'Checks URLs matching Sphinx linkcheck_ignore patterns in '
            'README.rst and documentation sources.'
        ),
    )
    parser.add_argument(
        '--timeout',
        type = float,
        default = 20.0,
        help = 'HTTP timeout in seconds. (default: 20)',
    )
    parser.add_argument(
        '--strict-access',
        action = 'store_true',
        help = (
            'Fail on HTTP 401/403 '
            '(by default these are treated as reachable).'
        ),
    )
    parser.add_argument(
        '--user-agent',
        default = 'mimeogram-link-verifier/1.0',
        help = 'User-Agent header value for requests.',
    )
    arguments = parser.parse_args( )

    root = Path( __file__ ).resolve( ).parents[ 2 ]
    conf_path = root / 'documentation' / 'conf.py'
    files = _iter_documentation_files( root )
    urls = _extract_urls_from_files( files )
    ignore_patterns = _load_linkcheck_ignore_patterns( conf_path )
    ignored_urls = _filter_ignored_urls( urls, ignore_patterns )

    print( f'Found {len( ignored_urls )} ignored URL(s) to verify.' )
    if not ignored_urls:
        print( 'No ignored URLs matched source files.' )
        return 0

    failures = 0
    for url in ignored_urls:
        result = _check_url(
            url = url,
            timeout = arguments.timeout,
            user_agent = arguments.user_agent,
            strict_access = arguments.strict_access,
        )
        status = str( result.status ) if result.status is not None else 'ERR'
        final = f' -> {result.final_url}' if result.final_url else ''
        verdict = 'OK' if result.ok else 'FAIL'
        print( f'[{verdict}] {status} {url}{final} ({result.note})' )
        if not result.ok: failures += 1

    if failures:
        print( f'Ignored-link verification failed for {failures} URL(s).' )
        return 1
    print( 'Ignored-link verification passed.' )
    return 0


if __name__ == '__main__':
    sys.exit( main( ) )
