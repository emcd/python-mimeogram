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
<https://emcd.github.io/documentation-common/v1/sphinx-html/common/conduct.html>`_
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

Requirements and Design
-------------------------------------------------------------------------------

* Review accepted capability requirements in ``openspec/specs/``. Manage new
  capabilities, breaking or cross-cutting changes, architectural shifts, and
  substantial performance or security work through OpenSpec changes in
  ``openspec/changes/``. Follow the project's OpenSpec workflow instructions
  and keep accepted specifications synchronized when changes are completed.

* Document stable subsystem architecture, design rationale, and local
  constraints in the nearest source-near README, normally
  ``sources/**/README.md``. Update the affected README when implementation
  structure or operational patterns change rather than recreating centralized
  architecture or specification mirrors under ``documentation/``.

Guidance and Standards
-------------------------------------------------------------------------------

* Follow the `development environment preparation and management instructions
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/environment.html>`_
  to ensure consistency with maintainer development environments and CI
  workflows.

* Configure Git commit signing as required for all contributions. See the
  `environment setup guide
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/environment.html#git-commit-signatures>`_
  for configuration details.

* Adhere to the `development practices
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/practices.html>`_,
  `code style
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/style.html>`_,
  and `testing guidelines
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/tests.html>`_
  to improve the probability of pull request acceptance. You may wish to use an
  LLM to assist with this, if the standards seem too onerous or specific.

* Also consider the `nomenclature advice
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/nomenclature.html>`_
  for consistency and to improve the probability of pull request acceptance.

* Run validation commands before submitting contributions. See the `validation
  guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/validation.html>`_
  for available commands and workflow. (If you installed the Git pre-commit and
  pre-push hooks during environment setup, then they will run the validations
  for you.)

* Prepare changelog fragments according to the `releases guide
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/releases.html>`_
  as appropriate.

* Although unnecessary for non-maintainer contributions, additional background
  can be found in the `maintenance guide
  <https://emcd.github.io/documentation-common/v1/sphinx-html/common/maintenance.html>`_.

Artificial Intelligence
-------------------------------------------------------------------------------

* Contributions, which are co-authored by large language models (LLMs), are
  welcome, provided that they adhere to the project guidance and standards
  above and are, otherwise, of good quality.

* A more compact representation of the above guidance and standards, plus some
  other advice for these models, can be found in
  ``.auxiliary/configuration/conventions.md``. You may link to this file from a
  ``AGENTS.md``, ``CLAUDE.md``, ``GEMINI.md``, ``CONVENTIONS.md``, etc... file
  in the root of the project. These files are ignored by Git as we do not wish
  to pollute the root of the project with them in the upstream repository.

Resources
-------------------------------------------------------------------------------

.. toctree::
   :maxdepth: 2

   Code of Conduct <https://emcd.github.io/documentation-common/v1/sphinx-html/common/conduct.html>
   devapi
   Environment Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/environment.html>
   Practices Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/practices.html>
   Code Style Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/style.html>
   Testing Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/tests.html>
   Nomenclature Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/nomenclature.html>
   Germanic Nomenclature Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/nomenclature-germanic.html>
   Validation Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/validation.html>
   Release Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/releases.html>
   Maintenance Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/maintenance.html>
   Architecture Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/architecture.html>
   Requirements Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/requirements.html>

.. Language-specific guides stay in a hidden toctree so Sphinx includes them
   in the site graph without adding renderer-specific navigation glue to the
   portable common Markdown sources.
.. toctree::
   :hidden:

   Python Environment Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/environment-python.html>
   Python Architecture Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/architecture-python.html>
   Python Development Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/practices-python.html>
   Rust Development Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/practices-rust.html>
   TOML Configuration Practices <https://emcd.github.io/documentation-common/v1/sphinx-html/common/practices-toml.html>
   Latin-derived Verb Vocabulary <https://emcd.github.io/documentation-common/v1/sphinx-html/common/nomenclature-latin.html>
   Python Automatic Formatting <https://emcd.github.io/documentation-common/v1/sphinx-html/common/python-autoformat.html>
   Python Testing Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/tests-python.html>
   Python Validation Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/validation-python.html>
   Python Release Guide <https://emcd.github.io/documentation-common/v1/sphinx-html/common/releases-python.html>
