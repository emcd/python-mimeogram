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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    python-mimeogram/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    ├── data/                    # Redistributable data resources
    ├── pyinstaller.spec         # Executable packaging configuration
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    ├── mimeogram/          # Main Python package
    │   ├── __/                      # Centralized import hub
    │   │   ├── __init__.py          # Re-exports core utilities
    │   │   ├── imports.py           # External library imports
    │   │   └── nomina.py            # python-mimeogram-specific naming constants
    │   ├── __init__.py              # Package entry point
    │   ├── py.typed                 # Type checking marker
    │   ├── __main__.py              # CLI entry point for `python -m mimeogram`
    │   ├── cli.py                   # Command-line interface implementation
    │   ├── exceptions.py            # Package exception hierarchy
    │   └── [modules].py             # Feature-specific modules
    

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

Component Integration
===============================================================================

CLI Implementation
-------------------------------------------------------------------------------

The command-line interface is organized for maintainability:

.. code-block::

    mimeogram/
    ├── __main__.py      # Entry point: `python -m mimeogram`
    └── cli.py           # CLI implementation and argument parsing

This separation allows the CLI logic to be imported and tested independently
while following Python's standard module execution pattern.

Exception Organization
-------------------------------------------------------------------------------

Package-wide exceptions are centralized in ``sources/mimeogram/exceptions.py``
following the standard hierarchy patterns documented in the `common practices guide
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_.

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation that architect agents can
evolve as the project grows. For questions about organizational principles,
subpackage patterns, or testing strategies, refer to the comprehensive common
documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
