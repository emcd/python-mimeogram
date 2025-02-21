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
CLI Examples
*******************************************************************************


Creating Mimeograms
===============================================================================

Basic File Bundling
-------------------------------------------------------------------------------

Bundle specific files into a mimeogram:

.. code-block:: bash

    mimeogram create src/*.py

Bundle multiple types of files, each with its content type detected:

.. code-block:: bash

    mimeogram create src/*.py README.rst

Recurse into subdirectories (subject to Git ignore rules):

.. code-block:: bash

    mimeogram create --recurse-directories=True src/ tests/

By default, the mimeogram will be copied to the clipboard. To print to stdout
instead:

.. code-block:: bash

    mimeogram create --clipboard=False src/*.py

Adding Context
-------------------------------------------------------------------------------

Add a message to provide context to the LLM:

.. code-block:: bash

    mimeogram create --edit-message src/*.py

For LLM interfaces without project support, include format instructions:

.. code-block:: bash

    mimeogram create --prepend-prompt src/*.py


Applying Mimeograms
===============================================================================

Basic File Unpacking
-------------------------------------------------------------------------------

Apply changes from clipboard (default):

.. code-block:: bash

    mimeogram apply

Apply changes from standard input:

.. code-block:: bash

    mimeogram apply --clipboard=False

Apply changes from file:

.. code-block:: bash

    mimeogram apply --clipboard=False changes.mimeogram

Apply changes relative to a different base directory than the current working
directory:

.. code-block:: bash

    mimeogram apply --base-directory /path/to/project

Apply changes in non-interactive mode:

.. code-block:: bash

    mimeogram apply --review-mode=silent /path/to/project


Interactive Review
-------------------------------------------------------------------------------

By default, when running on a terminal, you will be presented with interactive
review mode. For each file, you'll see a menu like this:

.. code-block:: text

    src/example.py [2.5K]
    Action? (a)pply, (d)iff, (e)dit, (i)gnore, (s)elect hunks, (v)iew >

Available actions:

- ``a``: Apply the proposed content as-is.
- ``d``: Show differences between current and proposed content.
- ``e``: Edit the proposed content.
- ``i``: Skip this file.
- ``s``: Interactively select which proposed changes to apply.
- ``v``: View the proposed content.

For protected paths, you'll see a modified menu:

.. code-block:: text

    ~/.config/sensitive.conf [1.2K] [PROTECTED]
    Action? (d)iff, (i)gnore, (p)ermit changes, (v)iew >

The ``p`` option lets you override protection for that specific file.

Using the Hunk Selector
-------------------------------------------------------------------------------

When using the ``s`` (select hunks) option, you'll review each change block:

.. code-block:: text

    @@ -1,5 +1,7 @@
     def example():
    -    return 42
    +    """Example function with docstring."""
    +    return 42

    Apply this change? (y)es, (n)o, (v)iew >

This lets you cherry-pick specific changes within each file.


Setting Project Instructions
===============================================================================

For LLM interfaces that support project-level instructions (like Claude.ai or
ChatGPT), you can setup the mimeogram format prompt once and reuse it
thereafter.

Copy instructions to clipboard (default behavior):

.. code-block:: bash

    mimeogram provide-prompt

Print to stdout instead:

.. code-block:: bash

    mimeogram provide-prompt --clipboard=False

Then paste these into your project instructions. All subsequent chats will
understand mimeograms without needing to include the format instructions in
each message.
