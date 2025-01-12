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
                                  python-mimeogram
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/python-mimeogram
   :alt: Package Version
   :target: https://pypi.org/project/python-mimeogram/

.. image:: https://img.shields.io/pypi/status/python-mimeogram
   :alt: PyPI - Status
   :target: https://pypi.org/project/python-mimeogram/

.. image:: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml

.. image:: https://emcd.github.io/python-mimeogram/coverage.svg
   :alt: Code Coverage Percentage
   :target: https://github.com/emcd/python-mimeogram/actions/workflows/tester.yaml

.. image:: https://img.shields.io/github/license/emcd/python-mimeogram
   :alt: Project License
   :target: https://github.com/emcd/python-mimeogram/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/python-mimeogram
   :alt: Python Versions
   :target: https://pypi.org/project/python-mimeogram/


What and Why
===============================================================================

Exchange hierarchical file collections with Large Language Models.

Motivation
-------------------------------------------------------------------------------

Cost and Efficiency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Cost optimization through GUI-based LLM services vs API billing
* Support for batch operations instead of file-by-file interactions

Technical Benefits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Preserves hierarchical directory structure
* Version control friendly
* Supports async workflows
* Enables automation through text processing

Flexibility and Accessibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* IDE and platform agnostic
* No premium subscriptions required
* Works with LLM GUIs lacking project functionality
* Can be used by CLIs and GUIs and passed directly via API

Limitations and Alternatives
-------------------------------------------------------------------------------

* LLMs must be prompted to understand and use mimeograms
* Manual refresh needed (no automatic sync)
* Cannot retract stale content from conversation history in provider GUIs
* Consider dedicated tools (e.g., Cursor) for tighter collaboration

Comparison
----------

+---------------------+-------------+------------+-------------+---------------+
| Feature             | Mimeograms  | Projects   | Direct API  | Specialized   |
|                     |             | (Web) [1]_ | Integration | IDEs [2]_     |
+=====================+=============+============+=============+===============+
| Cost Model          | Varies [3]_ | Flat rate  | Usage-based | Subscription  |
+---------------------+-------------+------------+-------------+---------------+
| Directory Structure | Yes         | No         | Yes [4]_    | Yes           |
+---------------------+-------------+------------+-------------+---------------+
| Real-time Updates   | No          | No         | Yes [4]_    | Yes           |
+---------------------+-------------+------------+-------------+---------------+
| IDE Integration     | Any         | Web only   | N/A         | N/A           |
+---------------------+-------------+------------+-------------+---------------+
| Setup Required      | CLI tool    | None       | SDK/Auth    | Full install  |
+---------------------+-------------+------------+-------------+---------------+
| Version Control     | Yes         | No         | Yes         | Yes           |
+---------------------+-------------+------------+-------------+---------------+
| Platform Support    | Universal   | Web        | Universal   | Limited       |
+---------------------+-------------+------------+-------------+---------------+
| Automation Support  | Yes         | No         | Yes         | Varies        |
+---------------------+-------------+------------+-------------+---------------+

.. [1] ChatGPT and Claude.ai subscription feature
.. [2] `Cursor <https://www.cursor.com/>`_, etc...
.. [3] Flat rate for GUI, usage-based for API
.. [4] Requires custom implementation

Notes:
- "Direct API Integration" refers to custom applications providing I/O tools
  for LLMs to use via APIs, such as the Anthropic or OpenAI API
- Cost differences can be significant at scale
- Real-time updates in specialized IDEs may require premium features


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



.. image:: https://img.shields.io/pypi/implementation/python-mimeogram
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/python-mimeogram/

.. image:: https://img.shields.io/pypi/wheel/python-mimeogram
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/python-mimeogram/
