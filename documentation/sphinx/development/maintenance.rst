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
Maintenance
*******************************************************************************

.. todo:: Github workflows for updating dependecies locks.


Copier
===============================================================================

The project was created from a `Copier template
<https://github.com/emcd/python-project-common/tree/master/template>`_. In
addition to seeding the initial project structure and code, updates from the
template can be incorporated into the project, ensuring adherence to evolving
practices and technologies.

Updates
-------------------------------------------------------------------------------

1. Ensure the working directory is clean (commit or stash changes).

2. Run the update command:
   ::

        copier update --answers-file .auxiliary/configuration/copier-answers.yaml

.. note:: The update process preserves your answers from the previous template
          generation. You can override specific answers using the ``--data``
          option with the update command.
