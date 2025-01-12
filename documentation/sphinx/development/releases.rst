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
Releases
*******************************************************************************

The project follows `semantic versioning <https://semver.org/>`_ for releases.

Release Process
===============================================================================

Initial Release Candidate
-------------------------------------------------------------------------------

1. Checkout ``master`` branch.

2. Pull from upstream to ensure all changes have been synced.

3. Checkout new release branch: ``release-<major>.<minor>``.

4. Bump alpha to release candidate. Commit.
   ::

        hatch --env develop version rc

5. Tag.
   ::

        git tag v${rc_version}

6. Push release branch and tag to upstream with tracking enabled.

7. Checkout ``master`` branch.

8. Bump alpha to next minor version on ``master`` branch. Commit.
   ::

        hatch --env develop version minor,alpha

9. Tag start of development for next release.
    ::

        git tag i${next_release_version}

Release
-------------------------------------------------------------------------------

1. Checkout release branch.

2. Bump release candidate to release. Commit.
   ::

        hatch --env develop version release

3. Run Towncrier. Commit.
   ::

        hatch --env develop run towncrier build --keep --version ${release_version}

4. Tag.
   ::

        git tag v${release_version}

5. Push release branch and tag to upstream.

6. Wait for the release workflow to complete successfully.

7. Clean up news fragments to prevent recycling in future releases. Commit.
   ::

        git rm documentation/towncrier/*.rst
        git commit -m "Clean up news fragments."

8. Push cleanup commit to upstream.

9. Cherry-pick Towncrier commits back to ``master`` branch.

Postrelease Patch
-------------------------------------------------------------------------------

1. Checkout release branch.

2. Develop and test patch against branch. Add Towncrier entry. Commit.

3. Bump release to patch or increment patch number. Commit.
   ::

        hatch --env develop version patch

4. Run Towncrier. Commit.
   ::

        hatch --env develop run towncrier build --keep --version ${patch_version}

5. Tag.
   ::

        git tag v${patch_version}

6. Push release branch and tag to upstream.

7. Wait for the release workflow to complete successfully.

8. Clean up news fragments to prevent recycling in future releases. Commit.
   ::

        git rm documentation/towncrier/*.rst
        git commit -m "Clean up news fragments."

9. Push cleanup commit to upstream.

10. Cherry-pick patch and Towncrier commits back to ``master`` branch,
    resolving conflicts as necessary.

Changelog Entries
===============================================================================

The project uses `Towncrier <https://towncrier.readthedocs.io/en/stable/>`_ to
manage its changelog. When making changes that should be noted in the
changelog, add a file ("fragment") to the ``documentation/towncrier`` directory
with of ``<issue_number>.<type>.rst``, for changes with a Github issue, or
``+<title>.<type>.rst``, for changes without an associated issue number.

The entries will be collected and organized when a release is made, as
described in the release process sections above.

Available Types
-------------------------------------------------------------------------------

* ``bugfix``: For bug fixes
* ``docs``: For documentation improvements
* ``feature``: For new features
* ``platform``: For changes to supported platforms
* ``removal``: For deprecations and removals

Format
-------------------------------------------------------------------------------

The file should contain a concise description of the change written in present
tense. For example:

.. code-block:: rst
   :caption: documentation/towncrier/+immutable-modules.feature.rst

   Add support for immutable module reclassification.

The description should:

* Start with a capital letter
* End with a period
* Use present tense (e.g., "Add", "Fix", "Update")
* Focus on the what and why, not the how
* Be understandable by users, not just developers

Examples
-------------------------------------------------------------------------------

Bug Fix:
    .. code-block:: rst
       :caption: documentation/towncrier/456.bugfix.rst

       Fix attribute visibility in immutable modules.

Documentation:
    .. code-block:: rst
       :caption: documentation/towncrier/457.docs.rst

       Improve release process documentation with Towncrier details.

Feature:
    .. code-block:: rst
       :caption: documentation/towncrier/458.feature.rst

       Add recursive module reclassification support.

Platform:
    .. code-block:: rst
       :caption: documentation/towncrier/459.platform.rst

       Add support for Python 3.13.

Removal:
    .. code-block:: rst
       :caption: documentation/towncrier/460.removal.rst

       Remove deprecated ``make_immutable`` function.
