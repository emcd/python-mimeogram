#!/usr/bin/env python3
"""Validate Towncrier news fragments for correct naming and reST syntax.

Checks fragment filenames against the type vocabulary defined in
pyproject.toml and validates reST markup via docutils. Name-first,
parse-second ordering ensures we skip docutils overhead for files
towncrier will never consume.
"""

import io as _io
import re as _re
import sys as _sys
from contextlib import redirect_stderr as _redirect_stderr
from pathlib import Path as _Path

try:
    import tomllib as _tomllib
except ModuleNotFoundError:
    import tomli as _tomllib  # type: ignore[import-untyped]

from docutils.core import publish_doctree as _publish_doctree


def load_towncrier_types(
    pyproject_path: _Path,
) -> list[ str ]:
    ''' Extracts fragment type directory names from pyproject.toml. '''
    with pyproject_path.open( 'rb' ) as f:
        config = _tomllib.load( f )
    types = config.get( 'tool', {} ).get( 'towncrier', {} ).get( 'type', [] )
    if isinstance( types, dict ):
        types = [ types ]
    return [ t[ 'directory' ] for t in types ]


def validate_fragment_names(
    fragments: list[ _Path ], types: list[ str ]
) -> tuple[ list[ str ], set[ _Path ] ]:
    ''' Validates fragment filenames against naming conventions.

        Returns (error_messages, invalid_paths).
    '''
    type_pattern = '|'.join( _re.escape( t ) for t in types )
    named_pattern = _re.compile(
        rf'^\+([\w][\w.-]*)\.({type_pattern})\.rst$' )
    issue_pattern = _re.compile(
        rf'^(\d+)\.({type_pattern})\.rst$' )
    errors: list[ str ] = []
    invalid: set[ _Path ] = set( )
    for frag in fragments:
        name = frag.name
        if not named_pattern.match( name ) \
            and not issue_pattern.match( name ):
            errors.append(
                f'{frag}: invalid fragment name. '
                f'Expected +<name>.<type>.rst or <issue>.<type>.rst '
                f'where type is one of: {", ".join( types )}' )
            invalid.add( frag )
    return errors, invalid


# Match default-role backticks (`text`) but not explicit roles
# (`:role:`text``) or literals (``text``).
_DEFAULT_ROLE_PATTERN = _re.compile(
    r'(?<!:)\`(?!`)([^`]+)\`(?!`)' )


def validate_fragment_syntax(
    fragments: list[ _Path ],
) -> list[ str ]:
    ''' Validates reST syntax of fragment files via docutils.

        Returns list of error messages for files with parse
        warnings/errors.
    '''
    errors: list[ str ] = []
    settings = {
        'report_level': 2,
        'halt_level': 5,
        'traceback': True,
    }
    for frag in fragments:
        with frag.open( ) as f:
            content = f.read( )
        backtick_matches = _DEFAULT_ROLE_PATTERN.findall( content )
        if backtick_matches:
            examples = ', '.join(
                f'`{m}`' for m in backtick_matches[ :3 ] )
            errors.append(
                f'{frag}: default-role backticks detected '
                f'({examples}). Use double backticks for code '
                f'literals or an explicit role like :code:`text`.' )
            continue
        stderr_capture = _io.StringIO( )
        try:
            with _redirect_stderr( stderr_capture ):
                _publish_doctree(
                    content, settings_overrides = settings )
        except Exception as exc:
            errors.append(
                f'{frag}: reST parse error: {exc}' )
            continue
        stderr_output = stderr_capture.getvalue( )
        if stderr_output:
            errors.append(
                f'{frag}: reST warnings:'
                f'\n{stderr_output.rstrip( )}' )
    return errors


def main( ) -> None:
    ''' Validates all towncrier fragments in the project. '''
    project_root = _Path.cwd( )
    pyproject_path = project_root / 'pyproject.toml'
    towncrier_dir = project_root / '.auxiliary' / 'data' / 'towncrier'
    if not towncrier_dir.is_dir( ):
        print(
            'No towncrier fragment directory found; '
            'nothing to validate.' )
        _sys.exit( 0 )
    fragments = sorted( towncrier_dir.glob( '*.rst' ) )
    if not fragments:
        print( 'No fragments found; nothing to validate.' )
        _sys.exit( 0 )
    types = load_towncrier_types( pyproject_path )
    if not types:
        print(
            'Error: no towncrier types found in pyproject.toml.',
            file = _sys.stderr )
        _sys.exit( 1 )
    errors: list[ str ] = [ ]
    name_errors, invalid_paths = validate_fragment_names(
        fragments, types )
    errors.extend( name_errors )
    valid_fragments = [
        f for f in fragments if f not in invalid_paths ]
    if valid_fragments:
        syntax_errors = validate_fragment_syntax( valid_fragments )
        errors.extend( syntax_errors )
    if errors:
        for err in errors:
            print( err, file = _sys.stderr )
        _sys.exit( 1 )
    for frag in fragments:
        print( f'{frag} OK' )


if __name__ == '__main__':
    main( )
