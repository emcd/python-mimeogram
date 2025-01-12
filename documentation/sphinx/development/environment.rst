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
Environment
*******************************************************************************

Initial Installation
===============================================================================

1. Ensure that you have installed `Git LFS <https://git-lfs.com/>`_.

2. Clone your fork of the repository.

3. Install Git LFS Git hooks in this repository:
   ::

        git lfs install

4. Ensure that you have installed `Pipx <https://pipx.pypa.io/stable/>`_.
   (If installing via ``pip``, you will want to use your system Python rather
   than the current global Python provided by Asdf, Mise, Pyenv, etc....)

5. Ensure that you have installed
   `Copier <https://copier.readthedocs.io/en/stable/>`_ and
   `Hatch <https://github.com/pypa/hatch/blob/master/README.md>`_ via Pipx:
   ::

        pipx install copier hatch

6. Install Git pre-commit and pre-push hooks:
   ::

        hatch --env develop run pre-commit install --config .auxiliary/configuration/pre-commit.yaml

Installation Updates
===============================================================================

1. Run:
   ::

        git pull

2. Remove the Hatch virtual environments:
   ::

        hatch env prune

Python Interpreter
===============================================================================

1. Run:
   ::

        hatch --env develop run python

Shell
===============================================================================

1. Run:
   ::

        hatch --env develop shell
