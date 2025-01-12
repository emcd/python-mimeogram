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
Nomenclature
*******************************************************************************

This guide presents naming conventions and patterns for Python and Rust
projects. The lists are not exhaustive, and new patterns may emerge for
specific domains or requirements.

When working with third-party APIs or established codebases, it may be
appropriate to follow their existing naming conventions rather than those
presented here. The goal is consistency within a given context rather than
rigid adherence to these patterns.


Classes
===============================================================================

General Guidance
-------------------------------------------------------------------------------

- Use ``Async`` suffix for asynchronous interfaces.

- Avoid ``Type`` suffix except when fitting to existing framework. I.e., do not
  follow the pattern in Python's ``types`` module unless there is good reason
  to do so.


Abstract Classes
-------------------------------------------------------------------------------

- Prefix with ``Abstract`` for abstract base classes.

- Use adjective names for interface-like classes when they describe
  capabilities.

.. code-block:: python

    class AbstractDictionary:
        ''' Abstract base for dictionary types. '''

    class Comparable:
        ''' Interface for objects supporting comparison. '''

    class Immutable:
        ''' Interface for objects preventing modification. '''


Base Classes
-------------------------------------------------------------------------------

- Use ``Base`` or ``Common`` suffix for base classes.

- Use ``Extension``/``Supplement`` (Latin-derived) or ``Mixin`` (Germanic-like)
  suffix for mix-in classes.

.. code-block:: python

    class DictionaryBase:
        ''' Base class for dictionary implementations. '''

    class LoggingMixin:
        ''' Adds logging capabilities to classes. '''


Container Classes
-------------------------------------------------------------------------------

Name based on behavior rather than implementation.

.. code-block:: python

    class ProducerDictionary:
        ''' Dictionary producing values on demand. '''

    class QueueAsync:
        ''' Queue with asynchronous interface. '''


Decorator Classes
-------------------------------------------------------------------------------

- Use adjectives when describing the modification.

- Use nouns when describing the resulting form.

.. code-block:: python

    class Comparable:
        ''' Decorator class providing comparison capabilities. '''

    class Dataclass:
        ''' Decorator class creating data class. '''


Enum Classes
-------------------------------------------------------------------------------

- Use plural nouns for enum class names.

- Use PascalCase for enum members to reflect singleton semantics.

.. code-block:: python

    class States:
        Initial = auto( )
        Execution = auto( )
        Complete = auto( )


Exception Classes
-------------------------------------------------------------------------------

- Follow standard hierarchy: ``Omniexception`` -> ``Omnierror`` -> specific
  exceptions.

- Use present tense verbs with these patterns:

    - ``[<Noun>]<Verb>Failure`` for operation failures
    - ``[<Noun>]<Verb>Interruption`` for interrupted operations
    - ``[<Noun>]<Verb>Invalidity`` for invalid states/data

- Use ``[<Noun>]<Property>Error`` for other error cases.

.. code-block:: python

    class ConfigureFailure( Omnierror ):
        ''' Raised when configuration fails. '''

    class AttributeInvalidity( Omnierror ):
        ''' Raised when attribute value is invalid. '''

    class ProcessInterruption( Omniexception ):
        ''' Raised when process is interrupted. '''


Metaclasses
-------------------------------------------------------------------------------

- Use ``Class``/``Factory`` (Latin-derived) or ``Builder``/``Maker``
  (Germanic-derived) suffix.

.. code-block:: python

    class ValidatorClass( type ):
        ''' Metaclass for creating validator classes. '''

    class SetBuilder( type ):
        ''' Metaclass for building set classes. '''


Special Purpose Classes
-------------------------------------------------------------------------------

Use appropriate suffix pairs based on purpose:

- ``Proxy`` (Latin-derived) or ``Wrapper`` (Germanic-derived) for delegation
  patterns
- ``Coordinator``/``Manager``/``Supervisor`` (Latin-derived) or ``Overseer``
  (Germanic-derived) for resource management
- ``Spectator``/``View`` for limited access patterns

.. code-block:: python

    class WeakrefWrapper:
        ''' Wraps object with weak reference semantics. '''

    class ConnectionManager:
        ''' Manages database connections. '''

    class DictionaryView:
        ''' Provides read-only view of dictionary. '''


Functions
===============================================================================

General Patterns
-------------------------------------------------------------------------------

``<verb>_<noun>``: Where verb describes the action and noun describes the
target.

``<preposition>_<noun>``: For methods only. Chainable operations typically
returning modified copies.

Noun Placeholders
-------------------------------------------------------------------------------

- ``<attribute>``: Named property or field of an object
- ``<component>``: Distinct part of a larger system or application
- ``<condition>``: Boolean predicate or state
- ``<data>``: Raw or structured information, regardless of location
- ``<execution>``: Execution context (process, thread, task) managed by current
  process
- ``<feature>``: Optional functionality that can be enabled/disabled
- ``<format>``: Data serialization format (JSON, XML, etc.)
- ``<future>``: Planned future execution
- ``<object>``: In-process entity (instance of a Python class)
- ``<reactor>``: Callback or event handler
- ``<reservation>``: Claim on future resource usage
- ``<resource>``: Entity external to the current process (file, network
  service, etc.)
- ``<service>``: Long-running process or daemon external to current process
- ``<space>``: Memory or storage allocation
- ``<type>``: Python type or class

Preposition Prefixes
-------------------------------------------------------------------------------

- ``as_<format-or-type>``: Returns copy of object in different format or type.
  Chainable with other methods.

- ``from_<format-or-type>``: Class method that constructs object from specific
  format or type.

- ``with_<attribute>``: Returns copy of object with modified attributes.
  Chainable with other methods.

Verb Prefixes
-------------------------------------------------------------------------------

- ``access_<object>``: Returns value via computed or indirect access (e.g.,
  property getter, descriptor protocol). For in-process objects only.

- ``acquire_<resource>``: Obtains exclusive access to shared resource requiring
  explicit release (e.g., mutex, database connection). Antonym:
  ``release_<resource>``.

- ``activate_<execution-or-service>``: Starts execution context or service. For
  both in-process executions and external services. Antonym:
  ``deactivate_<execution-or-service>``.

- ``allocate_<space>``: Reserves system memory or storage space for future use.
  Antonym: ``deallocate_<space>``.

- ``assess_<data>``: Examines data to derive insights or patterns.

- ``assert_<resource>`` [Python]: Verifies resource exists or condition holds,
  raising exception if not. [Rust]: Panics if condition fails. Related:
  ``verify_<condition>`` which returns boolean.

- ``calculate_<value>``: Computes value from one or more inputs using defined
  algorithm.

- ``cancel_<future-or-reservation>``: Revokes planned execution or resource
  claim. Antonym for both ``schedule_<execution>`` and ``reserve_<resource>``.
  See these related patterns for specific usage.

- ``configure_<component>``: Applies settings or parameters to component,
  preparing it for operation. Related: ``prepare_<component>`` for full
  initialization.

- ``create_<resource>``: Creates new resource external to current process
  (e.g., file, database table). For in-process object creation, see
  ``produce_<object>``. Antonym: ``delete_<resource>``.

- ``deactivate_<execution-or-service>``: Stops execution context or service.
  Antonym: ``activate_<execution-or-service>``.

- ``deallocate_<space>``: Frees previously allocated system memory or storage
  space. Antonym: ``allocate_<space>``.

- ``delete_<resource>``: Removes resource external to current process.
  [Python]: For in-process objects, we generally rely on garbage collection or
  context managers and do not need explicit destructors. Antonym:
  ``create_<resource>``.

- ``deregister_<reactor>``: Removes previously registered event handler or
  callback. Antonym: ``register_<reactor>``.

- ``disable_<feature>``: Deactivates optional feature or functionality.
  Antonym: ``enable_<feature>``.

- ``discover_<value>``: Detects or determines value from environment or
  context.

- ``display_<data>``: Presents data in user-facing format. Synonym:
  ``present_<data>``.

- ``enable_<feature>``: Activates optional feature or functionality. Antonym:
  ``disable_<feature>``.

- ``ensure_<resource>``: Creates resource if it doesn't exist, returns existing
  resource if it does. Related: ``create_<resource>`` for forced creation.

- ``examine_<resource>``: Retrieves metadata about resource without accessing
  full content (e.g., file stats, HTTP HEAD).

- ``filter_<objects>``: Returns subset of objects matching specified criteria.

- ``intercept_<exceptions>`` [Python]: Invokes functions while capturing their
  exceptions for later handling. Used primarily in concurrent execution
  contexts where multiple exceptions need collection.

- ``is_<member-or-state>``: Tests type membership or current state. Returns
  boolean. Related: ``verify_<condition>`` for condition verification.

- ``modify_<object>``: Updates in-process object state. Alternative to
  ``update_<resource>`` when context requires disambiguation between in-process
  and external modifications.

- ``parse_<format>``: Extracts structured data from formatted input (e.g.,
  JSON, XML).

- ``prepare_<component>``: Fully initializes component, including registration
  of handlers/extensions. Related: ``configure_<component>`` for settings
  application.

- ``probe_<resource>``: Tests resource accessibility or status. Returns boolean
  indicating availability. Related: ``verify_<condition>`` for more thorough
  verification.

- ``produce_<object>``: Creates new instance in process memory. For external
  resource creation, see ``create_<resource>``.

- ``query_<resource>``: Performs structured data retrieval with parameters or
  filters. Related: ``retrieve_<resource>`` for simpler data access.

- ``register_<reactor>``: Adds event handler or callback to registry. Antonym:
  ``deregister_<reactor>``.

- ``release_<resource>``: Releases previously acquired shared resource.
  Antonym: ``acquire_<resource>``.

- ``render_<template>``: Produces output by combining template with data.

- ``report_<data>``: Collates data from analyses or diverse sources into a
  structured or human-readable form.

- ``request_<action>``: Initiates asynchronous operation, typically on remote
  service. Returns future or promise representing eventual completion.

- ``reserve_<resource>``: Claims resource for future use. Related to
  ``schedule_<execution>``; both use ``cancel_<future-or-reservation>`` as
  antonym.

- ``restore_<object>``: Deserializes object from persistent storage. Related:
  ``save_<object>`` for serialization.

- ``retrieve_<resource>``: Obtains copy of data from external resource. No
  release required. Related: ``query_<resource>`` for parameterized retrieval.

- ``save_<object>``: Serializes object to persistent storage. Related:
  ``restore_<object>`` for deserialization.

- ``schedule_<execution>``: Plans future execution of task or process. Related
  to ``reserve_<resource>``; both use ``cancel_<future-or-reservation>`` as
  antonym.

- ``survey_<resource>``: Lists or enumerates members of external resource
  collection.

- ``test_<assertion>``: Verifies specific assertion about code behavior. Note:
  Only for use in test suites, not in public interfaces.

- ``transform_<data>``: Changes data structure or format. Synonym:
  ``convert_<data>``.

- ``update_<resource>``: Modifies state of external resource. For in-process
  objects, consider ``modify_<object>`` when disambiguation is needed.

- ``validate_<object>`` [Python]: Returns object if valid, raises exception if
  invalid. [Rust]: Returns ``Result::Ok`` containing object if valid else
  ``Result::Err``. Related: ``verify_<condition>`` which returns boolean
  if a condition is satisfied.

- ``verify_<condition>``: Tests condition or state. Returns boolean. Related:
  ``validate_<object>``, which returns object or raises exception,
  ``is_<member-or-state>`` for type/state testing.

Function Suffixes
-------------------------------------------------------------------------------

The project uses a limited set of function suffixes to indicate specific
execution patterns:

- ``_async``: Indicates asynchronous execution
- ``_continuous``: Indicates generator/iterator return type (alternative:
  ``_streaming`` when using Germanic-derived terms)
- ``_recursive``: Indicates recursive execution when this is part of the
  function's contract rather than an implementation detail

Other execution patterns (parallel processing, batch operations, etc.) are
better expressed through specific function names or appropriate use of
threading/multiprocessing facilities.

When Not to Use Suffixes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Avoid suffixes for:

- Implementation details (``_cached``, ``_optimized``)
- Alternative implementations (``_safe``, ``_fallback``)
- Batch operations (use prefix ``mass_`` or ``multi_`` prefixes instead)
- In-place operations (use Python's established patterns like list methods)
- Development status (``_experimental``)
- Debugging aids (``_verbose``)
- Parallel processing (use appropriate concurrency primitives instead)

These aspects are better handled through:

- Separate, clearly named functions
- Documentation of performance characteristics
- Version control and release management
- Logging and debugging facilities
- Threading and multiprocessing facilities


Linguistic Consistency
===============================================================================

The project generally uses Latin-derived terms for both class and function
names. This preference arises from:

- Prevalence of Latin-derived terms in computer science
- More precise technical meanings in Latin-derived terms
- Larger vocabulary of available terms

Germanic-derived and Greek-derived terms may be appropriate when maintaining
linguistic consistency within:

- Related function names
- Class hierarchies
- Enum members
- Module-level names

Within individual names, maintain agreement between verbs and nouns:

- ``shape_set`` (Germanic-derived verb with Germanic-derived noun)
- ``validate_sequence`` (Latin-derived verb with Latin-derived noun)
- ``analyze_algorithm`` (Greek-derived verb with Greek-influenced noun)

Technical abbreviations (``str``, ``obj``), acronyms (``xml``, ``json``), and
some portmanteau words are linguistically neutral and can be used with terms
from any linguistic derivation.

When in doubt, prefer Latin-derived terms as the project default.


Latin-to-Germanic Verb Mappings
-------------------------------------------------------------------------------

The following table provides Germanic alternatives to Latin-derived verbs.
These are provided primarily for reference and for cases where linguistic
consistency with Germanic nouns is desired.

+-----------------+------------------+----------------------------------------+
| Latin-derived   | Germanic-derived | Notes                                  |
+=================+==================+========================================+
| access          | get              |                                        |
+-----------------+------------------+----------------------------------------+
| acquire         | grab             | Common in technical phrases            |
+-----------------+------------------+----------------------------------------+
| activate        | start            |                                        |
+-----------------+------------------+----------------------------------------+
| allocate        | slot             |                                        |
+-----------------+------------------+----------------------------------------+
| assess          | weigh            | Is there a better synonym?             |
+-----------------+------------------+----------------------------------------+
| assert          | swear            | Is there a better synonym?             |
+-----------------+------------------+----------------------------------------+
| calculate       | reckon           |                                        |
+-----------------+------------------+----------------------------------------+
| cancel          | stop             |                                        |
+-----------------+------------------+----------------------------------------+
| configure       | setup            | Compound from "set up"                 |
+-----------------+------------------+----------------------------------------+
| create          | make             |                                        |
+-----------------+------------------+----------------------------------------+
| deactivate      | stop             |                                        |
+-----------------+------------------+----------------------------------------+
| deallocate      | free             |                                        |
+-----------------+------------------+----------------------------------------+
| delete          | kill             |                                        |
+-----------------+------------------+----------------------------------------+
| deregister      | unenroll         | Germanic ``un-`` prefix pattern        |
+-----------------+------------------+----------------------------------------+
| disable         | unswitch         | Neologism; pairs with ``switch``       |
+-----------------+------------------+----------------------------------------+
| discover        | find             |                                        |
+-----------------+------------------+----------------------------------------+
| display         | show             |                                        |
+-----------------+------------------+----------------------------------------+
| enable          | switch           | Pairs with ``unswitch``                |
+-----------------+------------------+----------------------------------------+
| ensure          | righten          | Slightly archaic                       |
+-----------------+------------------+----------------------------------------+
| examine         | sniff            | Informal but established in tech       |
+-----------------+------------------+----------------------------------------+
| filter          | sift             |                                        |
+-----------------+------------------+----------------------------------------+
| intercept       | catch            |                                        |
+-----------------+------------------+----------------------------------------+
| modify          | change           |                                        |
+-----------------+------------------+----------------------------------------+
| parse           | split            |                                        |
+-----------------+------------------+----------------------------------------+
| prepare         | ready            | Used as verb not adjective             |
+-----------------+------------------+----------------------------------------+
| probe           | ping             | From network terminology               |
+-----------------+------------------+----------------------------------------+
| produce         | new              | Verb; familiar to ``C++`` programmers  |
+-----------------+------------------+----------------------------------------+
| query           | ask              |                                        |
+-----------------+------------------+----------------------------------------+
| register        | enroll           |                                        |
+-----------------+------------------+----------------------------------------+
| release         | free             |                                        |
+-----------------+------------------+----------------------------------------+
| render          | fillin / mold    | Compound from "fill in"                |
+-----------------+------------------+----------------------------------------+
| report          | tell             |                                        |
+-----------------+------------------+----------------------------------------+
| request         | ask              | Same as ``query`` mapping              |
+-----------------+------------------+----------------------------------------+
| reserve         | earmark          |                                        |
+-----------------+------------------+----------------------------------------+
| restore         | load             | Common pair with ``dump``              |
+-----------------+------------------+----------------------------------------+
| retrieve        | fetch            |                                        |
+-----------------+------------------+----------------------------------------+
| save            | dump             | Common pair with ``load``              |
+-----------------+------------------+----------------------------------------+
| schedule        | handoff          | Compound from "hand off"               |
+-----------------+------------------+----------------------------------------+
| survey          | list             |                                        |
+-----------------+------------------+----------------------------------------+
| transform       | shape            | Avoids Latin ``re-`` prefix            |
+-----------------+------------------+----------------------------------------+
| update          | freshen          |                                        |
+-----------------+------------------+----------------------------------------+
| validate        | sound            | Archaic but precise meaning            |
+-----------------+------------------+----------------------------------------+
| verify          | truth            | Used as verb: "to tell truth"          |
+-----------------+------------------+----------------------------------------+
