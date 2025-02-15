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

    # Bundle Python files from src directory
    mimeogram create src/*.py

    # Bundle multiple file types
    mimeogram create src/*.py tests/*.py README.rst

    # Bundle with recursion into directories
    mimeogram create --recurse-directories=True src/ tests/

By default, the mimeogram will be copied to the clipboard. To print to stdout
instead:

.. code-block:: bash

    # Print to stdout instead of copying to clipboard
    mimeogram create --clipboard=False src/*.py

Adding Context
-------------------------------------------------------------------------------

Add a message to provide context to the LLM:

.. code-block:: bash

    # Opens your default editor for message input
    mimeogram create --edit-message src/*.py

For LLM interfaces without project support, include format instructions:

.. code-block:: bash

    # Add format instructions before mimeogram
    mimeogram create --prepend-prompt src/*.py

    # Combine with message
    mimeogram create --edit-message --prepend-prompt src/*.py


Applying Mimeograms
===============================================================================

Non-Interactive Application
-------------------------------------------------------------------------------

Apply changes without review (suitable for scripts or CI):

.. code-block:: bash

    # Apply from clipboard (default)
    mimeogram apply

    # Apply from stdin
    mimeogram apply --clipboard=False

    # Apply from file
    mimeogram apply --clipboard=False changes.mimeogram

    # Apply to different base directory
    mimeogram apply --base-directory /path/to/project

Interactive Review
-------------------------------------------------------------------------------

By default, when running on a terminal, mimeogram will enter interactive review
mode. For each file, you'll see a menu like this:

.. code-block:: text

    src/example.py [2.5K]
    Action? (a)pply, (d)iff, (e)dit, (i)gnore, (s)elect hunks, (v)iew >

Available actions:

- ``a``: Apply the changes as-is
- ``d``: Show diff between current and proposed content
- ``e``: Edit the proposed content
- ``i``: Skip this file
- ``s``: Interactively select which changes to apply
- ``v``: View the proposed content

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
ChatGPT), you can set up mimeogram format instructions once:

.. code-block:: bash

    # Copy instructions to clipboard (default behavior)
    mimeogram provide-prompt

    # Print to stdout instead
    mimeogram provide-prompt --clipboard=False

Then paste these into your project instructions. All subsequent chats will
understand mimeograms without needing to include the format instructions in
each message.


Common Workflows
===============================================================================

Code Review
-------------------------------------------------------------------------------

When asking an LLM to review code:

.. code-block:: bash

    # Bundle files with context
    mimeogram create --edit-message src/*.py tests/*.py

    # Paste into LLM chat
    # ... interact with LLM ...

    # Apply suggested changes interactively
    mimeogram apply

Project Setup
-------------------------------------------------------------------------------

When getting help setting up a new project:

.. code-block:: bash

    # Set format instructions in project
    mimeogram provide-prompt
    # Paste into project instructions

    # Send current project state
    mimeogram create --recurse-directories=True .
    # Paste into chat

    # Apply scaffolding interactively
    mimeogram apply

Bug Investigation
-------------------------------------------------------------------------------

When getting help with a bug:

.. code-block:: bash

    # Bundle relevant files with explanation
    mimeogram create --edit-message src/buggy.py tests/test_buggy.py

    # After LLM suggests fixes
    mimeogram apply

    # Select specific hunks if the fix is partially correct
    # Use 's' in the interactive menu
