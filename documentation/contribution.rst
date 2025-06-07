.. vim: set filetype=rst fileencoding=utf-8:
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


:tocdepth: 3


*******************************************************************************
Contribution
*******************************************************************************

Contribution to this project is welcome! However, it must follow the `code of
conduct
<https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/conduct.rst>`_
for the project.


Ways to Contribute
===============================================================================

* File bug reports and feature requests in the `issue tracker
  <https://github.com/emcd/python-mimeogram/issues>`_. (Please try
  to avoid duplicate issues.)

* Fork the repository and submit `pull requests
  <https://github.com/emcd/python-mimeogram/pulls>`_ to improve the
  source code or documentation. Pull requests should follow the development
  guidance and standards below.


Development
===============================================================================

Guidance and Standards
-------------------------------------------------------------------------------

* Follow the `development environment preparation and management instructions
  <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/environment.rst>`_
  to ensure consistency with maintainer development environments and CI
  workflows.

* Adhere to the `development practices
  <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/practices.rst>`_
  and `code style <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/style.rst>`_
  to improve the probability of pull request acceptance. You may wish to use an
  LLM to assist with this, if the standards seem too onerous or specific.

* Also consider the `nomenclature advice
  <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/nomenclature.rst>`_
  for consistency and to improve the probability of pull request acceptance.

* Prepare changelog fragments according to the `releases guide
  <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/releases.rst>`_
  as appropriate.

* Although unncessary for non-maintainer contributions, additional background
  can be found in the `maintenance guide
  <https://github.com/emcd/python-project-common/blob/docs-1/documentation/common/maintenance.rst>`_.

Artificial Intelligence
-------------------------------------------------------------------------------

* Contributions, which are co-authored by large language models (LLMs), are
  welcome, provided that they adhere to the project guidance and standards
  above and are, otherwise, of good quality.

* A more compact representation of the above guidance and standards, plus some
  other advice for these models, can be found in
  ``.auxiliary/configuration/conventions.md``. You may link to this file from a
  ``AGENTS.md``, ``CLAUDE.md``, ``CONVENTIONS.md`` file in the root of the
  project. These files are ignored by Git as we do not wish to pollute the
  root of the project with them in the upstream repository.

Resources
-------------------------------------------------------------------------------

.. toctree::
   :maxdepth: 2

   devapi
