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


''' File content updates. '''


from __future__ import annotations

import enum
from pathlib import Path

from . import __


class UpdateError(Exception):
    """Base class for update-related errors."""


class Action(enum.Enum):
    """Available actions for each part in interactive mode."""
    APPLY = 'apply'     # Write the part to filesystem
    DIFF = 'diff'       # Show changes
    EDIT = 'edit'       # Edit in $EDITOR
    IGNORE = 'ignore'   # Skip this part
    VIEW = 'view'       # Display in pager


class AtomicUpdater:
    """Handles atomic file updates with rollback support."""

    def __init__(self):
        self.backups = {}  # Maps paths to original content
        self.updated = []  # Tracks successful updates in order

    async def backup_file(self, path: Path) -> None:
        """Create backup if file exists."""
        if path.exists():
            async with __.aiofiles.open(path, 'r', encoding='utf-8') as f:
                self.backups[path] = await f.read()

    async def write_file(
        self,
        path: Path,
        content: str,
        mode: str = 'w',
        encoding: str = 'utf-8'
    ) -> None:
        """Write content to file atomically."""
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        try:
            # Write to temp file first
            async with __.aiofiles.open(temp_path, mode, encoding=encoding) as f:
                await f.write(content)

            # Use os.replace for atomic operation
            import os
            os.replace(str(temp_path), str(path))
        finally:
            # Clean up temp file if something went wrong
            if temp_path.exists():
                temp_path.unlink()

    async def rollback(self) -> None:
        """Restore files in reverse order of updates."""
        import logging
        logger = logging.getLogger(__name__)

        for path in reversed(self.updated):
            try:
                if path in self.backups:
                    await self.write_file(path, self.backups[path])
                else:
                    path.unlink()
            except Exception as e:
                logger.error('Rollback failed for %s: %s', path, e)


class Updater:
    """Updates filesystem with mimeogram part contents."""

    def __init__(self, *, interactive: bool = True):
        self.interactive = interactive
        self.atomic = AtomicUpdater()

    def _get_path(
        self,
        location: str,
        base_path: __.typx.Optional[Path] = None
    ) -> Path:
        """Get a path for a part location.

        Args:
            location: Part location (URL or path)
            base_path: Optional base path for relative paths

        Returns:
            Path object (not resolved)

        Raises:
            UpdateError: If location is a URL or path is invalid
        """
        # Skip editor message parts
        if location.startswith('mimeogram://'):
            raise UpdateError(f'Cannot write special location: {location}')

        # Handle relative vs absolute paths
        path = Path(location)
        if not path.is_absolute() and base_path is not None:
            path = base_path / path

        return path

    async def _show_diff(self, part: ParsedPart, target: Path) -> None:
        """Show differences between current content and target file.

        Args:
            part: Part being processed
            target: Target path for this part
        """
        import difflib
        import tempfile
        import subprocess

        # Prepare inputs for diff
        from_lines = []
        to_lines = part.content.splitlines(keepends=True)
        from_file = '/dev/null'
        to_file = str(target)

        if target.exists():
            try:
                async with __.aiofiles.open(target, 'r', encoding=part.charset) as f:
                    content = await f.read()
                    from_lines = content.splitlines(keepends=True)
                    from_file = str(target)
            except Exception as e:
                raise UpdateError(f"Failed to read existing file: {e}") from e

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=from_file,
            tofile=to_file,
            lineterm=''
        ))

        if not diff_lines:
            print("No changes")
            return

        # Show diff in pager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.diff') as tmp:
            tmp.writelines(line + '\n' for line in diff_lines)
            tmp.flush()

            # Try to use $PAGER, fall back to less or more
            import os
            pager = os.environ.get('PAGER', 'less')
            if not pager:
                pager = 'less'

            try:
                subprocess.run([pager, tmp.name], check=True)
            except subprocess.CalledProcessError:
                # If less fails, try more
                if pager == 'less':
                    subprocess.run(['more', tmp.name], check=True)
            except FileNotFoundError:
                # If no pager available, just print
                print(''.join(diff_lines))
                input("Press Enter to continue...")

    async def _edit_content(self, part: ParsedPart) -> __.typx.Optional[str]:
        """Edit part content in system editor.

        Args:
            part: Part to edit

        Returns:
            Modified content if edited, None if unchanged
        """
        from .editor import EditorInterface

        # Get suffix from location for proper syntax highlighting
        suffix = Path(part.location).suffix or '.txt'

        try:
            edited = EditorInterface.read_message(part.content, suffix=suffix)
            if edited != part.content:
                return edited
            return None
        except Exception as e:
            raise UpdateError(f"Failed to edit content: {e}") from e

    async def _view_content(self, part: ParsedPart) -> None:
        """Display part content in pager.

        Args:
            part: Part to display
        """
        import tempfile
        import subprocess

        # Create temp file for pager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as tmp:
            tmp.write(part.content)
            tmp.flush()

            # Try to use $PAGER, fall back to less or more
            import os
            pager = os.environ.get('PAGER', 'less')
            if not pager:
                pager = 'less'

            try:
                subprocess.run([pager, tmp.name], check=True)
            except subprocess.CalledProcessError:
                # If less fails, try more
                if pager == 'less':
                    subprocess.run(['more', tmp.name], check=True)
            except FileNotFoundError:
                # If no pager available, just print
                print(part.content)
                input("Press Enter to continue...")

    async def _prompt_action(self, part: ParsedPart, target: Path) -> tuple[Action, str]:
        """Prompt user for action on this part.

        Args:
            part: Part being processed
            target: Target path for this part

        Returns:
            Tuple of (selected action, content to write)
            Content will be None if action is IGNORE or unchanged after EDIT

        Raises:
            UpdateError: If user cancels with EOF or interrupt
        """
        # Check if we can do interactive input
        import sys
        if not sys.stdin.isatty():
            # Default to APPLY if we can't prompt
            return Action.APPLY, part.content

        content = part.content
        while True:
            # One-line status with shortcuts
            print(f"{part.location:<30} [{len(content)} bytes] : (a)pply, (d)iff, (e)dit, (i)gnore, (v)iew", end='')

            try:
                choice = input(" > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()  # Add newline after ^C or ^D
                raise UpdateError("User cancelled operation")

            # Handle single-letter shortcuts
            if choice in ('a', 'apply'):
                return Action.APPLY, content
            elif choice in ('d', 'diff'):
                await self._show_diff(part, target)
                continue  # Show prompt again after diff
            elif choice in ('e', 'edit'):
                edited = await self._edit_content(part)
                if edited is not None:
                    content = edited
                continue  # Show prompt again after editing
            elif choice in ('i', 'ignore'):
                return Action.IGNORE, None
            elif choice in ('v', 'view'):
                await self._view_content(part)
                continue  # Show prompt again after viewing
            else:
                print(f"Invalid choice: {choice}", end='')
                continue

    async def update(
        self,
        parts: __.cabc.Sequence[ParsedPart],
        base_path: __.typx.Optional[Path] = None,
        *,
        force: bool = False
    ) -> None:
        """Update filesystem with content from parts.

        Args:
            parts: Sequence of parts to process
            base_path: Optional base path for relative locations
            force: Currently unused (will be used for protection checks)

        Raises:
            UpdateError: If update fails
        """
        import logging
        logger = logging.getLogger(__name__)

        success = False
        try:
            for part in parts:
                # Skip editor messages
                if part.location.startswith('mimeogram://'):
                    logger.debug('Skipping editor message: %s', part.location)
                    continue

                try:
                    target = self._get_path(part.location, base_path)
                except Exception as e:
                    raise UpdateError(f'Invalid path {part.location}: {e}') from e

                # In interactive mode, prompt for action
                if self.interactive:
                    action, content = await self._prompt_action(part, target)
                    if action == Action.IGNORE:
                        logger.debug('User chose to ignore part: %s', part.location)
                        continue
                    if content is not None:
                        part.content = content

                # Create parent directories
                target.parent.mkdir(parents=True, exist_ok=True)

                # Backup existing file
                await self.atomic.backup_file(target)

                # Write new content
                logger.debug('Writing %d bytes to %s', len(part.content), target)
                await self.atomic.write_file(
                    target,
                    part.content,
                    encoding=part.charset
                )
                self.atomic.updated.append(target)

            success = True

        finally:
            if not success:
                logger.debug('Update failed, initiating rollback')
                await self.atomic.rollback()
