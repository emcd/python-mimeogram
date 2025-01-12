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

from pathlib import Path

from . import __
from .acquirers import ContentFetcher
from .editor import EditorInterface
from .format import MimeogramFormatter
from .parser import Parser, ParserError
from .updater import Updater, UpdateError
from .exceptions import MimeogramError, EmptyMimeogramError


def copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard.

    Note:
        Silently fails if pyperclip is not installed
    """
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning('pyperclip not installed. Clipboard copy unavailable.')


async def create_mimeogram(args: __.typx.Any) -> int:
    """Create a mimeogram from files and/or message.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    import logging
    logger = logging.getLogger(__name__)

    message = None
    if args.editor_message:
        try:
            message = EditorInterface.read_message()
        except MimeogramError as e:
            logger.error('Failed to capture message: %s', str(e))
            return 1

    try:
        async with ContentFetcher(strict=args.strict) as fetcher:
            parts = await fetcher.fetch_sources(args.sources, recursive=args.recursive)
            bundle = MimeogramFormatter.format_bundle(parts, message=message)

            print(bundle)

            if args.clip:
                copy_to_clipboard(bundle)

        return 0

    except EmptyMimeogramError:
        logger.error('No content to bundle - no files were processed and no message was provided')
        return 1
    except MimeogramError as e:
        logger.error('Failed to create bundle: %s', str(e))
        return 1
    except Exception as e:
        logger.error('Unexpected error: %s', str(e))
        return 1


async def apply_mimeogram(args: __.typx.Any) -> int:
    """Apply a mimeogram to the filesystem.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Read input from clipboard if specified
        if args.clip:
            try:
                import pyperclip
                content = pyperclip.paste()
                if not content:
                    logger.error('Clipboard is empty')
                    return 1
                logger.debug('Read %d characters from clipboard', len(content))
            except ImportError:
                logger.error('pyperclip not installed. Clipboard access unavailable.')
                return 1
        # Otherwise read from file or stdin
        else:
            if args.input == '-':
                import sys
                content = sys.stdin.read()
            else:
                async with __.aiofiles.open(args.input, 'r') as f:
                    content = await f.read()

        # Parse mimeogram
        try:
            parts = Parser.parse(content)
        except ParserError as e:
            logger.error('Failed to parse mimeogram: %s', str(e))
            return 1

        # Create updater with specified options
        updater = Updater(interactive=args.interactive)

        # Apply parts
        try:
            await updater.update(
                parts,
                base_path=args.base_path,
                force=args.force
            )
            logger.info('Successfully applied mimeogram')
            return 0
        except UpdateError as e:
            logger.error('Failed to apply mimeogram: %s', str(e))
            return 1

    except Exception as e:
        logger.error('Unexpected error: %s', str(e))
        return 1


async def main(args: __.typx.Optional[__.cabc.Sequence[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        args: Optional command line arguments (uses sys.argv if not provided)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    import argparse
    import logging
    import sys

    # Set up logging
    logger = logging.getLogger(__name__)

    # Create main parser
    parser = argparse.ArgumentParser(
        description='Create and apply mimeogram bundles.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Create subparsers
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
        type=Path,
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

    # Parse arguments
    args = parser.parse_args(args)

    # Configure logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(name)s:%(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(message)s'
        )

    # Dispatch to appropriate handler
    if args.command == 'create':
        return await create_mimeogram(args)
    elif args.command == 'apply':
        return await apply_mimeogram(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    import asyncio
    import sys
    sys.exit(asyncio.run(main()))
