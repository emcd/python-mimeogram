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
Operation
*******************************************************************************


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
* --force
    Override protections against potentially dangerous writes.
* --review-mode silent
    Apply all parts without review.


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

* You may not need to ask the LLM to create a return mimeogram to apply if you
  are using Claude artifacts, ChatGPT canvases, or similar. You can simply copy
  the final results and paste them into an editor buffer.

  * This saves tokens.
  * However, interactively applying a mimeogram has the advantage of allowing
    you to select hunks of a diff to apply, rather than the whole LLM-revised
    content.
  * Similarly, interactive application allows you to edit content in cases
    where it is not quite correct but also not worth more conversation rounds
    with the LLM.


Troubleshooting 🔍
===============================================================================

Possible Issues
-------------------------------------------------------------------------------

* **Clipboard Operations Fail**: Check if your clipboard manager is running and
  accessible. On Linux, ensure ``xclip`` or ``xsel`` is installed.

* **Oversized Mimeograms**: If LLMs truncate responses:
    * Reduce the number of files per mimeogram.
    * Split changes across multiple conversations.
    * Focus on smaller, atomic changes.

* **Invalid Part Errors**: If parts fail to apply:
    * Check file permissions.
    * Verify file paths are correct relative to working directory.
    * Use ``--base`` option to set correct base directory.
