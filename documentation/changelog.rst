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
