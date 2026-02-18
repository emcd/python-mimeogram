.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

mimeogram 1.6 (2026-02-18)
==========================

Enhancements
------------

- Acquisition: Use Detextive 3.1 decode_inform for MIME type, charset, and line-separator detection, including BOM-aware UTF-8 charset reporting for round trips.
- Add Python 3.14 and PyPy 3.11 support.
- CLI: Add --no-ignores flag to disable gitignore filtering during file collection. When gitignore filtering is enabled (default), warnings are emitted for skipped files with guidance to use --no-ignores flag.
- Integrate Detextive 2.0 for MIME type and charset detection, replacing internal detection with standardized library. This may produce normalized charset names (e.g., 'iso8859-9' instead of 'iso-8859-9') and treats empty files as valid text.
- Packaging: Publish Linux aarch64 standalone executables in GitHub releases.


Repairs
-------

- CLI: Disallow explicit None values for optional boolean flags and show {True,False} choices in help text.
- CLI: Fix parser error that prevented the application from running.
- CLI: Fix version command to work without requiring --application.name argument.
- CLI: Prevent Linux/X11 clipboard operations from hanging when xclip forks to the background.


Mimeogram 1.5 (2025-07-27)
==========================

Enhancements
------------

- Acquirers: Improve detection of files with textual content.


Mimeogram 1.4 (2025-07-05)
==========================

Enhancements
------------

- Add deterministic boundary option for reproducible mimeogram output. When
  enabled via ``--deterministic-boundary`` CLI flag or ``deterministic-boundary``
  configuration setting, boundaries are generated from content hashes instead of
  random UUIDs, making output diff-friendly for version control workflows.
  (Feature request from @developingjames.)
- Call ``finalize_module`` instead of ``reclassify_modules`` to improve
  documentation by applying Dynadoc to it.


Repairs
-------

- Replace call to ``reclassify_modules`` with ``finalize_module`` to address
  deprecation warning.


Mimeogram 1.3 (2025-06-06)
==========================

Enhancements
------------

- Internals update - nothing to see here. Lock versions of some dependencies in
  anticipation of breaking changes.


Mimeogram 1.2 (2025-03-29)
==========================

Bugfixes
--------

- Character set decoding error was raised when unable to detect line separator.
  Now, a warning is issued and the OS-native line separator is assumed.
- Release 1.1 executables were broken due to incomplete bundling of ``tiktoken``
  dependencies. Completely bundle these. (Bug report from @wad11656.)


Features
--------

- Ignore macOS ``.DS_Store`` file, regardless of whether it is listed in
  ``.gitignore`` or whether there is a ``.gitignore`` when collecting files from
  a directory.

  Likewise, ignore ``.env`` when collecting files from a directory. (For
  security reasons, as there may be secrets in it.)

  One can still explicitly specify ignored files to include them in mimeograms.
  Ignoring only applies to collecting files from directories, when directories
  are given as arguments to ``mimeogram create``.


Mimeogram 1.1 (2025-03-02)
==========================

Features
--------

- Support reporting of total token counts for mimeograms as part of ``mimeogram
  create`` output.


Supported Platforms
-------------------

- Add support for PyPy 3.10.


Mimeogram 1.0 (2025-02-22)
==========================

Features
--------

- Add Git ignore rule integration to avoid processing unwanted files.
- Add ``mimeogram apply`` command with interactive review, hunk selection, file
  editing, and atomic file updates.
- Add ``mimeogram create`` command for bundling files into clipboard-ready
  documents with preserved directory structure, Git ignore rule support, and
  integrated message editing.
- Add ``mimeogram provide-prompt`` command for generating format instructions
  and setting up LLM project-level support.
- Add atomic file updates with automatic rollback on errors.
- Add filesystem protection system to prevent accidental modification of
  sensitive paths.


Supported Platforms
-------------------

- Add support for CPython 3.10 through 3.13.
