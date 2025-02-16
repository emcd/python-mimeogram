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
                                  mimeogram
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/mimeogram
   :alt: Package Version
   :target: https://pypi.org/project/mimeogram/

.. image:: https://img.shields.io/pypi/status/mimeogram
   :alt: PyPI - Status
   :target: https://pypi.org/project/mimeogram/

.. image:: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-mimeogram/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-mimeogram
   :alt: Project License
   :target: https://github.com/emcd/python-mimeogram/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/mimeogram
   :alt: Python Versions
   :target: https://pypi.org/project/mimeogram/

.. image:: https://raw.githubusercontent.com/emcd/python-mimeogram/master/data/pictures/logo.svg
   :alt: Mimeogram Logo
   :width: 800
   :align: center


📨 A command-line tool for **exchanging collections of files with Large
Language Models** - bundle multiple files into a single clipboard-ready
document while preserving directory structure and metadata... good for code
reviews, project sharing, and LLM interactions.


Key Features ⭐
===============================================================================

* 📋 **Clipboard Integration**: Seamless copying and pasting by default.
* 🗂️ **Directory Structure**: Preserves hierarchical file organization.
* 🔄 **Interactive Reviews**: Review and apply proposed changes one by one.
* 🤖 **LLM Integration**: Built-in prompts and format instructions.
* 🛡️ **Path Protection**: Safeguards against dangerous modifications.


Installation 📦
===============================================================================

Standalone Executable (Recommended)
-------------------------------------------------------------------------------

Download the latest standalone executable for your platform from `GitHub
Releases <https://github.com/emcd/python-mimeogram/releases>`_. These
executables have no dependencies and work out of the box.

Python Package
-------------------------------------------------------------------------------

Executables Environment Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install with `pipx <https://pipx.pypa.io/stable/installation/>`_:

::

    pipx install mimeogram

(Pipx is preferred because it helps ensure that you have access to the
``mimeogram`` executable througout your system rather than in any specific
virtual environment.)


Package Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install with `uv <https://github.com/astral-sh/uv/blob/main/README.md>`_:

::

    uv pip install mimeogram

Or, install with ``pip``:

::

    pip install mimeogram


Examples 💡
===============================================================================

Working with LLM Interfaces (no project support)
-------------------------------------------------------------------------------

Use with Deepseek.com, API workbenches, GUIs which do not support projects,
etc...:

.. code-block:: bash

    # Bundle files with mimeogram format instructions into clipboard.
    mimeogram create src/*.py tests/*.py --prepend-prompt

    # Interact with LLM until you are ready to apply results.

    # Request mimeogram from LLM and copy it from browser to clipboard.

    # Apply mimeogram parts from clipboard.
    # (On terminal, this will be interactive by default.)
    mimeogram apply


Working with LLM Project GUIs
-------------------------------------------------------------------------------

E.g., Claude.ai or ChatGPT.com with models which support projects:

.. code-block:: bash

    # Copy mimeogram format instructions into clipboard.
    mimeogram provide-prompt

    # Paste mimeogram instructions into project instructions.

    # Any new chats will be able to reuse the project instructions.

.. code-block:: bash

    # Simply create mimeograms for new chats without prepending instructions.
    mimeogram create src/*.py tests/*.py

    # Same workflow as chats without project support at this point.


Command Options 🛠️
===============================================================================

Use ``--help`` with the ``mimeogram`` command or any of its subcommands to see
a full list of possible arguments:

.. code-block:: bash

    mimeogram --help

.. code-block:: bash

    mimeogram apply --help

Etc...


Create Command
-------------------------------------------------------------------------------

Bundle files into clipboard:

.. code-block:: bash

    mimeogram create [OPTIONS] SOURCES...

📋 Common options:

* --edit, -e
    Add message via editor.
* --prepend-prompt
    Include LLM instructions before mimeogram.
* --recurse, -r
    Include subdirectories and their contents. (Subject to Git ignore rules.)


Apply Command
-------------------------------------------------------------------------------

Apply changes from clipboard:

.. code-block:: bash

    mimeogram apply [OPTIONS]

📋 Common options:

* --base DIRECTORY
    Set base directory for relative paths in parts. (Working directory by
    default.)
* --mode silent
    Apply all parts without review.
* --force
    Override protections against potentially dangerous writes.


Configuration 🔧
===============================================================================

Default Location
-------------------------------------------------------------------------------

Mimeogram creates a configuration file on first run. You can find it at:

* Linux: ``~/.config/mimeogram/general.toml``
* macOS: ``~/Library/Application Support/mimeogram/general.toml``
* Windows: ``%LOCALAPPDATA%\\mimeogram\\general.toml``

Default Settings
-------------------------------------------------------------------------------

.. code-block:: toml

    [apply]
    from-clipboard = true    # Read from clipboard by default

    [create]
    to-clipboard = true      # Copy to clipboard by default

    [prompt]
    to-clipboard = true      # Copy prompts to clipboard

    [acquire-parts]
    fail-on-invalid = false  # Skip invalid files
    recurse-directories = false

    [update-parts]
    disable-protections = false


Best Practices 💫
===============================================================================

* Use ``--edit`` flag with ``create`` command to provide context to LLM. This
  has the advantage of letting you use a favorite editor to form a message to
  the LLM rather than a web GUI text area.
* Keep changes focused and atomic. Chats with sprawling changes may be cause
  LLM output windows to be exceeded when generating return mimeograms.
* Submit related files together. Fewer conversation rounds related to shuffling
  mimeograms mean more conversation rounds for productive discussion.
* If the platform supports projects, set project instructions from ``mimeogram
  provide-prompt``. These will be reused across all chats in the project,
  making every one of its chats a mimeogram-aware one.
* You may not need to create a return mimeogram to apply if you are using
  Claude artifacts, ChatGPT canvases, or similar. You can simply copy the
  final results and paste them into an editor buffer. This will save tokens.
  However, interactively applying a mimeogram has the advantage of allowing you
  to select hunks of a diff to apply, rather than the whole diff.


Motivation 🎯
===============================================================================

Cost and Efficiency 💰
-------------------------------------------------------------------------------
* Cost optimization through GUI-based LLM services vs API billing.
* Support for batch operations instead of file-by-file interactions.

Technical Benefits ✅
-------------------------------------------------------------------------------
* Preserves hierarchical directory structure.
* Version control friendly. (I.e., honors Git ignore files.)
* Supports async/batch workflows.

Platform Neutrality ☁️
-------------------------------------------------------------------------------
* IDE and platform agnostic.
* No premium subscriptions required.
* Works with LLM GUIs lacking project functionality.

Limitations and Alternatives 🔀
===============================================================================

* LLMs must be prompted to understand and use mimeograms.
* Manual refresh of files needed (no automatic sync).
* Cannot retract stale content from conversation history in provider GUIs.
* Consider dedicated tools (e.g., Cursor) for tighter collaboration loops.

Comparison ⚖️
-------------------------------------------------------------------------------

+---------------------+------------+------------+-------------+--------------+
| Feature             | Mimeograms | Projects   | Direct API  | Specialized  |
|                     |            | (Web) [1]_ | Integration | IDEs [2]_    |
+=====================+============+============+=============+==============+
| Cost Model          | Flat rate  | Flat rate  | Usage-based | Flat rate    |
+---------------------+------------+------------+-------------+--------------+
| Directory Structure | Yes        | No         | Yes [3]_    | Yes          |
+---------------------+------------+------------+-------------+--------------+
| IDE Integration     | Any        | Web only   | N/A         | One          |
+---------------------+------------+------------+-------------+--------------+
| Setup Required      | CLI tool   | None       | SDK/Auth    | Full install |
+---------------------+------------+------------+-------------+--------------+
| Version Control     | Yes        | No         | Yes [3]_    | Yes          |
+---------------------+------------+------------+-------------+--------------+
| Platform Support    | Universal  | Web        | Universal   | Limited      |
+---------------------+------------+------------+-------------+--------------+
| Automation Support  | Yes        | No         | Yes         | Varies       |
+---------------------+------------+------------+-------------+--------------+

.. [1] ChatGPT and Claude.ai subscription feature
.. [2] `Cursor <https://www.cursor.com/>`_, etc...
.. [3] Requires custom implementation

Notes:

- "Direct API Integration" refers to custom applications providing I/O tools
  for LLMs to use via APIs, such as the Anthropic or OpenAI API.
- Cost differences can be significant at scale, especially when considering
  cache misses against APIs.


About the Name 📝
===============================================================================

The name "mimeogram" draws from multiple sources:

* 📜 From Ancient Greek roots:
    * μῖμος (*mîmos*, "mimic") + -γραμμα (*-gramma*, "written character, that
      which is drawn")
    * Like *mimeograph* but emphasizing textual rather than pictorial content.

* 📨 From **MIME** (Multipurpose Internet Mail Extensions):
    * Follows naming patterns from the Golden Age of Branding: Ford
      Cruise-o-matic, Ronco Veg-O-Matic, etc....
    * Reflects the MIME-inspired bundle format.

* 📬 Echoes *telegram*:
    * Emphasizes message transmission.
    * Suggests structured communication.

Note: Despite similar etymology, this project is distinct from the PyPI package
*mimeograph*, which serves different purposes.

Pronunciation? The one similar to *mimeograph* seems to roll off the tongue
more smoothly, though it is one more syllable than "mime-o-gram". Preferred
IPA: /ˈmɪm.i.ˌoʊ.ɡræm/.


`More Flair <https://www.imdb.com/title/tt0151804/characters/nm0431918>`_
===============================================================================

.. image:: https://img.shields.io/github/last-commit/emcd/python-mimeogram
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-mimeogram

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json
   :alt: Copier
   :target: https://github.com/copier-org/copier

.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
   :alt: Hatch
   :target: https://github.com/pypa/hatch

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :alt: pre-commit
   :target: https://github.com/pre-commit/pre-commit

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
   :alt: Bandit
   :target: https://github.com/PyCQA/bandit

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :alt: Pylint
   :target: https://github.com/pylint-dev/pylint

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :alt: Pyright
   :target: https://microsoft.github.io/pyright

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :alt: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
   :alt: Hypothesis
   :target: https://hypothesis.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/implementation/mimeogram
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/mimeogram/

.. image:: https://img.shields.io/pypi/wheel/mimeogram
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/mimeogram/
