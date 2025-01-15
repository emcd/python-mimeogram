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


''' Command-line interface for mimeogram. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe(__name__)


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    import logging

    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(name)s:%(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(message)s'
        )


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        _scribe.warning('pyperclip not installed. Clipboard copy unavailable.')
        return False


@__.dataclass
class CreateCommand:
    """Parameters for create command."""
    sources: list[str]
    recursive: bool = False
    strict: bool = False
    clip: bool = False
    editor_message: bool = False


@__.dataclass
class ApplyCommand:
    """Parameters for apply command."""
    input: str
    clip: bool = False
    base_path: __.typx.Optional[__.Path] = None
    interactive: bool = False
    force: bool = False
    dry_run: bool = False


async def read_input(cmd: ApplyCommand) -> __.typx.Optional[str]:
    """Read input from clipboard, file, or stdin."""
    if cmd.clip:
        try:
            import pyperclip
            content = pyperclip.paste()
            if not content:
                _scribe.error('Clipboard is empty')
                return None
            _scribe.debug('Read %d characters from clipboard', len(content))
            return content
        except ImportError:
            _scribe.error('pyperclip not installed. Clipboard access unavailable.')
            return None
    else:
        if cmd.input == '-':
            return __.sys.stdin.read()
        else:
            async with __.aiofiles.open(cmd.input, 'r') as f:
                return await f.read()


async def handle_create(cmd: CreateCommand) -> int:
    """Handle create command."""
    from .acquirers import ContentFetcher
    from .exceptions import MimeogramError
    from .format import format_bundle
    if cmd.editor_message:
        try:
            from .editor import read_message
            message = read_message()
        except MimeogramError as exc:
            _scribe.error('Failed to capture message: %s', exc)
            return 1
    else: message = None
    try:
        async with ContentFetcher(strict=cmd.strict) as fetcher:
            parts = await fetcher.fetch_sources(
                cmd.sources,
                recursive=cmd.recursive
            )
            bundle = format_bundle(parts, message=message)
            print(bundle)
            if cmd.clip and not copy_to_clipboard(bundle): return 1
            return 0
    except MimeogramError as exc:
        _scribe.error('Failed to create bundle: %s', exc)
        return 1


async def handle_apply(cmd: ApplyCommand) -> int:
    """Handle apply command."""
    from .exceptions import MimeogramError
    from .parser import parse_bundle
    from .updater import Updater
    try:
        content = await read_input(cmd)
        if not content: return 1
        parts = parse_bundle(content)
        updater = Updater(interactive=cmd.interactive)
        await updater.update(
            parts,
            base_path=cmd.base_path,
            force=cmd.force
        )
        _scribe.info('Successfully applied mimeogram')
        return 0
    except MimeogramError as exc:
        _scribe.error('Failed to apply mimeogram: %s', exc)
        return 1


def create_parser() -> __.typx.Any:
    """Create argument parser."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Create and apply mimeogram bundles.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        required=True
    )

    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create a mimeogram bundle from files/URLs'
    )
    create_parser.add_argument(
        'sources',
        nargs='*',
        help='File paths or URLs. If none provided, requires --editor-message.'
    )
    create_parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='Recurse into directories'
    )
    create_parser.add_argument(
        '-s',
        '--strict',
        action='store_true',
        help='Fail on first non-textual file or URL instead of skipping'
    )
    create_parser.add_argument(
        '--clip',
        action='store_true',
        help='Copy the final bundle to clipboard'
    )
    create_parser.add_argument(
        '--editor-message',
        action='store_true',
        help='Spawn editor to capture an initial message part'
    )

    # Apply command
    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply a mimeogram bundle to filesystem'
    )
    apply_parser.add_argument(
        'input',
        nargs='?',
        default='-',
        help='Input file (default: stdin if --clip not specified)'
    )
    apply_parser.add_argument(
        '--clip',
        action='store_true',
        help='Read mimeogram from clipboard instead of file/stdin'
    )
    apply_parser.add_argument(
        '--base-path',
        type=__.Path,
        help='Base path for relative locations'
    )
    apply_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Prompt for action on each part'
    )
    apply_parser.add_argument(
        '--force',
        action='store_true',
        help='Override protected path checks'
    )
    apply_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )

    return parser


async def main(args: __.typx.Optional[__.cabc.Sequence[str]] = None) -> int:
    """CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    setup_logging(parsed_args.verbose)
    match parsed_args.command:
        case 'create':
            return await handle_create(CreateCommand(
                sources=parsed_args.sources,
                recursive=parsed_args.recursive,
                strict=parsed_args.strict,
                clip=parsed_args.clip,
                editor_message=parsed_args.editor_message
            ))
        case 'apply':
            return await handle_apply(ApplyCommand(
                input=parsed_args.input,
                clip=parsed_args.clip,
                base_path=parsed_args.base_path,
                interactive=parsed_args.interactive,
                force=parsed_args.force,
                dry_run=parsed_args.dry_run
            ))
        case _:
            parser.print_help()
            return 1


if __name__ == '__main__': __.sys.exit(__.asyncio.run(main()))
