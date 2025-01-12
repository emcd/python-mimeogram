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
Practices
*******************************************************************************

Documentation
===============================================================================

* (**Python**) Documentation must be written as Sphinx reStructuredText. The
  docstrings for functions must not include parameter or return type
  documentation. Parameter and return type documentation is handled via
  :pep:`727` annotations. Pull requests, which include Markdown documentation
  or which attempt to provide function docstrings in the style of Google,
  NumPy, Sphinx, etc..., will be rejected.



* Use long option names, whenever possible, in command line examples. Readers,
  who are unfamiliar with a command, should not have to look up the meanings of
  single-character option names.

Exceptional Conditions
===============================================================================

* (**Python**) Allow reaonably-anticipated exceptions from the Python
  interpreter and standard library to pass through the application programming
  interface boundary. E.g., ``AttributeError``, ``KeyError``, etc.... Raise an
  exception, defined in the package, for any failure condition that arises from
  the use of the package features that are part of the interfaces of its Python
  object types or functions.

* (**Python**) Never swallow exceptions. Either chain a ``__cause__`` with a
  ``from`` original exception or raise a new exception with original exception
  as the ``__context__``. Or properly handle the exception.



Imports
===============================================================================

* (**Python**) Avoid ancillary imports into a module namespace. Instead, place
  common imports into the `__` package base or import at the function level.
  This avoids pollution of the module namespace, which should only have public
  attributes which relate to the interface that it is providing. This also
  makes functions more relocatable, since they carry their dependencies with
  them rather than rely on imports within the module which houses them.

Quality Assurance
===============================================================================

* Be sure to install the Git hooks, as mentioned in the ``Environment:
  Installation`` section. This will save you turnaround time from pull request
  validation failures.

* Maintain or improve the current level of code coverage. Even if code coverage
  is at 100%, consider cases which are not explicitly tested.
