---
allowed-tools: Bash(hatch --env develop run:*), Bash(git:*), LS, Read, Glob, Grep, Edit, MultiEdit, Write, WebFetch
description: Systematically conform Python code to project style and practice standards
---

# Python Code Conformance

For bringing existing Python code into full compliance with project standards.

Target code: `$ARGUMENTS`

**CRITICAL**: Focus on style/practice conformance, not functionality changes.

## Context

- Current git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`

## Prerequisites

- **MANDATORY**: Read project documentation guides first:
    - https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst
    - https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/style.rst
    - https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/nomenclature.rst
- Understand target files to be conformed
- Have read `CLAUDE.md` for project-specific guidance

## Priority Conformance Issues

### 1. Function Parameters: Wide Types
**Issue:** Using narrow concrete types instead of wide abstract types for parameters
**Before:**
```python
def process_items( items: list[ str ], config: dict[ str, int ] ) -> bool:
    return all( validate( item, config ) for item in items )
```
**After:**
```python
def process_items(
    items: __.cabc.Sequence[ str ],
    config: __.cabc.Mapping[ str, int ],
) -> bool:
    return all( validate( item, config ) for item in items )
```

### 2. Import Organization: Namespace Pollution
**Issue:** Polluting module namespace instead of using private aliases
**Before:**
```python
from pathlib import Path
from collections import defaultdict
import json
from typing import Any, Dict, List
```
**After:**
```python
# Direct imports when performance is a consideration
from json import loads as _json_loads

# Use __ subpackage for common imports
from . import __
```

### 3. Module Organization
**Issue:** Wrong order of module contents
**Should follow this order:**
1. Imports (see practices guide)
2. Common type aliases (`TypeAlias` declarations)
3. Private variables/functions for defaults (grouped semantically)
4. Public classes and functions (alphabetical)
5. All other private functions (alphabetical)

### 4. Spacing and Delimiters
**Issue:** Missing spaces in delimiters, operators
**Before:**
```python
def func(arg1,arg2="default"):
    result=process(arg1,{"key":"value"})
```
**After:**
```python
def func( arg1, arg2 = 'default' ):
    result = process( arg1, { 'key': 'value' } )
```

### 5. Type Annotations: Missing or Incomplete
**Issue:** Missing annotations, not using `TypeAlias` for complex types
**Before:**
```python
def process_user( user, callback=None ):
    return callback( user ) if callback else str( user )
```
**After:**
```python
UserRecord: __.typx.TypeAlias = dict[ str, str | int | list[ str ] ]

def process_user(
    user: UserRecord,
    callback: __.Absential[
        __.cabc.Callable[ [ UserRecord ], str ]
    ] = __.absent
) -> str:
    if not __.is_absent( callback ): return callback( user )
    return str( user )
```

### 6. Exception Handling: Overly Broad Blocks
**Issue:** Wrapping entire functions in try blocks
**Before:**
```python
def process_items( items: list[ str ] ) -> list[ dict ]:
    try:
        results = [ ]
        for item in items:
            validated = validate_item( item )  # Can raise
            processed = expensive_computation( validated )
            results.append( processed )
        return results
    except ValidationError:
        return [ ]
```
**After:**
```python
def process_items( items: __.cabc.Sequence[ str ] ) -> list[ dict ]:
    results = [ ]
    for item in items:
        try: validated = validate_item( item )  # Only risky statement
        except ValidationError:
            logger.warning( f"Skipping invalid item: {item}." )
            continue
        processed = expensive_computation( validated )
        results.append( processed )
    return results
```

### 7. Docstring Format and Mood
**Issue:** Wrong quotes, spacing, imperative mood
**Before:**
```python
def process_data( data ):
    """Process the input data."""  # Wrong quotes, imperative mood
```
**After:**
```python
def process_data(
    data: __.cabc.Sequence[ __.typx.Any ]
) -> dict[ str, __.typx.Any ]:
    ''' Processes input data and returns results. '''  # Narrative mood
```

### 8. Immutability: Using Mutable When Unnecessary
**Issue:** Using mutable containers when immutable would suffice
**Before:**
```python
def calculate_stats( data: list[ int ] ) -> dict[ str, float ]:
    results = { }
    results[ 'mean' ] = sum( data ) / len( data )
    return results
```
**After:**
```python
def calculate_stats(
    data: __.cabc.Sequence[ int ]
) -> __.immut.Dictionary[ str, float ]:
    return __.immut.Dictionary(
        mean = sum( data ) / len( data ),
        maximum = max( data ),
        minimum = min( data )
    )
```

## Conformance Process

### 1. Analysis Phase
- Read the three documentation guides thoroughly
- Examine target files to understand current state
- Run linters to identify specific violations
- Identify architectural patterns that need updating

### 2. Systematic Correction
Apply fixes in this order:
1. **Module Organization**: Reorder imports, type aliases, functions per practices guide
2. **Wide/Narrow Types**: Convert function parameters to wide abstract types
3. **Import Cleanup**: Remove namespace pollution, use private aliases and __ subpackage
4. **Type Annotations**: Add missing hints, create `TypeAlias` for complex types
5. **Exception Handling**: Narrow try block scope, ensure proper chaining
6. **Immutability**: Replace mutable with immutable containers where appropriate
7. **Spacing/Delimiters**: Fix `( )`, `[ ]`, `{ }` patterns
8. **Docstrings**: Triple single quotes, narrative mood, proper spacing
9. **Line Length**: Split at 79 columns using parentheses

### 3. Validation
```bash
hatch --env develop run linters  # Must pass clean
hatch --env develop run testers  # Must not break functionality
```

## Safety Requirements

**HALT if:**
- Linters reveal complex architectural issues
- Changes would alter functionality
- Type annotations conflict with runtime behavior
- Import changes break dependencies
- Tests start failing

**Your responsibilities:**
- Maintain exact functionality while improving practices/style
- Use project patterns consistently per the guides
- Reference all three guides for complex cases
- Verify all changes with linters and tests

## Success Criteria

- [ ] All linting violations resolved
- [ ] Module organization follows practices guide structure
- [ ] Function parameters use wide abstract types
- [ ] Imports avoid namespace pollution
- [ ] Type annotations comprehensive with `TypeAlias` usage
- [ ] Exception handling uses narrow try blocks
- [ ] Immutable containers used where appropriate
- [ ] No functionality changes
- [ ] Tests continue to pass
- [ ] Code follows all style guide patterns

**Note**: Always run full validation (`hatch --env develop run linters && hatch
--env develop run testers`) before considering the task complete.

## Final Report

Upon completion, provide a brief report covering:
- Specific conformance issues corrected (categorized by the priority issues above)
- Number of files modified
- Any patterns that required manual intervention
- Linter status before/after
- Any deviations from guides and justification
