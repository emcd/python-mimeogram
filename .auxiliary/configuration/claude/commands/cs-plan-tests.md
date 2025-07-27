---
allowed-tools: Bash(hatch --env develop run:*), Bash(git status), Bash(git log:*), Bash(echo:*), Bash(ls:*), Bash(find:*), LS, Read, Glob, Grep, Write, Edit, WebFetch
description: Analyze test coverage gaps and create comprehensive test implementation plan
---

# Plan Tests

**NOTE: This is an experimental workflow! If anything seems unclear or missing,
please stop for consultation with the user.**

For systematic analysis of test coverage gaps and creation of detailed test
implementation plans following project testing guidelines.

Target module/functionality: `$ARGUMENTS`

**CRITICAL**: Focus on analysis and planning only - do NOT implement tests.
**HALT if**:
- No target module or functionality is provided
- Target code cannot be analyzed
- Coverage data is unavailable

## Context

- Current git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- **CRITICAL - Current test coverage**: !`hatch --env develop run coverage report --show-missing`
- Existing test structure: !`find tests -name "*.py" | head -20`
- Test README status: !`ls tests/README.md 2>/dev/null && echo "Present" || echo "Missing"`

## Prerequisites

Ensure that you:
- Have access to target code modules for analysis
- Can generate current coverage reports
- Have read any relevant `CLAUDE.md` file
- Understand the [test-writing guidelines](https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst)

## Safety Requirements

**CRITICAL**: You MUST halt the process and consult with the user if ANY of the
following occur:

- **Missing Coverage Data**: If coverage reports cannot be generated
- **Inaccessible Code**: If target modules cannot be read or analyzed
- **Architecture Conflicts**: If analysis reveals fundamental testability issues
- **Documentation Access Issues**: If test guidelines cannot be accessed
- **Network Test Temptation**: NEVER plan tests against real external sites (example.com, httpbin.com, etc.)

**Your responsibilities:**
- Focus entirely on analysis and planning - NO implementation
- Create comprehensive, actionable test plans WITHOUT code snippets of test implementations
- Brief third-party library examples (e.g., httpx mock transport) are acceptable if researched
- Identify all coverage gaps systematically
- Consider project testing principles in planning
- Produce clear, structured planning artifacts
- Acknowledge immutability constraints - modules under test CANNOT be monkey-patched
- Test private functions/methods via public API - understand why if this fails

## Test Planning Process

Execute the following steps for target: `$ARGUMENTS`

### 0. Pre-Flight Verification
**MANDATORY - Access test-writing guidelines:**

Use WebFetch to access and read the complete testing guidelines:
https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst

**CRITICAL**: You MUST successfully access and understand the guide before
proceeding. If WebFetch fails, HALT and consult with the user.

### 1. Coverage Analysis Phase

**Generate and analyze current coverage data:**

```bash
hatch --env develop run coverage report --show-missing
hatch --env develop run coverage html
```

**CRITICAL ANALYSIS REQUIREMENTS:**
- Identify all uncovered lines in target modules
- Analyze which functions/classes lack any tests
- Determine which code paths are partially covered
- Note any pragma directives (# pragma: no cover) and their rationale

**For each target module:**
- Read the source code to understand the public API
- Identify all functions, classes, and methods
- Map uncovered lines to specific functionality
- Note dependency injection points and testability patterns

### 2. Gap Identification Phase

**Systematically catalog what needs testing:**

**Functionality Gaps:**
- Functions with zero test coverage
- Classes with untested methods
- Error handling paths not exercised
- Edge cases not covered

**Coverage Gaps:**
- Specific line numbers needing coverage
- Branch conditions not tested
- Exception handling paths missed
- Integration scenarios untested

**Architecture Gaps:**
- Code that requires dependency injection for testability
- Components that need filesystem mocking
- External service interactions requiring test doubles
- Private functions/methods not exercisable via public API
- Areas where full coverage may require violating immutability constraints
- Test data requirements (fixtures, snapshots, fake packages for `tests/data/`)

### 3. Test Strategy Development

**For each identified gap, determine:**

**Test Approach:**
- Which testing patterns apply (dependency injection, pyfakefs, etc.)
- What test doubles or fixtures are needed
- How to structure tests for maximum coverage

**Test Categories:**
- Basic functionality tests (000-099 range)
- Component-specific tests (100+ blocks per function/class/method)
- Edge cases and error handling (integrated within component blocks)

**Implementation Considerations:**
- Dependencies that need injection
- Filesystem operations requiring pyfakefs
- External services needing mocking (NEVER test against real external sites)
- Test data and fixtures needed under `tests/data/`
- Performance considerations

### 4. Test Organization Planning

**Determine test structure and numbering:**

**Review existing test numbering conventions:**
- Analyze current test file naming patterns
- Identify next available number blocks for new test modules
- Plan numbering for new test functions within modules

**CRITICAL - Test Module vs Function Numbering:**
- **Test modules**: Named as `test_<N>00_<module>.py` (e.g., `test_100_exceptions.py`, `test_500_cli.py`)
- **Test functions**: Within modules use 000-099 basic, 100+ blocks per component
- These are DIFFERENT numbering schemes - do not confuse them

**Test Module Numbering Hierarchy:**
- Lower-level functionality gets lower numbers (e.g., `test_100_exceptions.py`, `test_110_utilities.py`)
- Higher-level functionality gets higher numbers (e.g., `test_500_cli.py`, `test_600_server.py`)
- Subpackage modules: `test_<M><N>0_<subpackage>_<module>.py` where N advances by 10 within subpackage

**Update tests/README.md:**
- If missing, create it with test module numbering scheme
- If present, update it for any new test modules being planned
- Include project-specific testing conventions
- Document rationale for any pattern exceptions
- **IMPORTANT**: Update this file during planning, not during implementation

### 5. Plan Documentation Creation

**Create comprehensive test plan document:**

Save the plan to `.auxiliary/notes/test-plan-[sanitized-module-name].md` with:

**Plan Structure:**
```markdown
# Test Plan: [Module Name]

## Coverage Analysis Summary
- Current coverage: X%
- Target coverage: 100%
- Uncovered lines: [specific line numbers]
- Missing functionality tests: [list]

## Test Strategy

### Basic Functionality Tests (000-099)
- [List planned tests with brief descriptions]

### Component-Specific Tests (100+ blocks)
#### Function/Class/Method: [name] (Tests 100-199)
- [Planned test descriptions including happy path, edge cases, and error handling]
- [Dependencies needing injection]
- [Special considerations]

## Implementation Notes
- Dependencies requiring injection: [list]
- Filesystem operations needing pyfakefs: [list]
- External services requiring mocking: [list - NEVER test against real external sites]
- Test data and fixtures: [needed under tests/data/ - fake packages, snapshots, captured artifacts]
- Private functions/methods not testable via public API: [list with analysis]
- Areas requiring immutability constraint violations: [list with recommendations]
- Third-party testing patterns to research: [e.g., httpx mock transport]
- Test module numbering for new files: [following hierarchy conventions]
- Anti-patterns to avoid: [specific warnings including external network calls]

## Success Metrics
- Target line coverage: [percentage]
- Branch coverage goals: [percentage]
- Specific gaps to close: [line numbers]
```

### 6. Plan Validation

**Review and validate the plan:**

**Completeness Check:**
- All uncovered lines addressed
- All functions/classes have test strategy
- Error paths and edge cases included
- Integration scenarios covered

**Feasibility Check:**
- All planned tests align with project principles
- No monkey-patching of internal code required
- Dependency injection patterns are viable
- Performance considerations addressed

**Numbering Check:**
- Test numbering follows project conventions
- No conflicts with existing test numbers
- Logical organization by test type

## Success Criteria

Planning is complete when:
- [ ] Complete coverage analysis performed
- [ ] All testing gaps systematically identified
- [ ] Test strategy developed for each gap
- [ ] Test organization and numbering planned
- [ ] tests/README.md created or updated as needed
- [ ] Comprehensive plan document created
- [ ] Plan validates against project testing principles
- [ ] Implementation approach is clear and actionable

## Final Report

Upon completion, provide a brief summary covering:
- Current coverage percentage and specific gaps identified
- Number of new tests planned by category
- Key architectural considerations (dependency injection needs, etc.)
- **CRITICAL ASSESSMENT**: Areas where 100% coverage may be impossible without violating immutability constraints
- **PUSHBACK RECOMMENDATIONS**: Suggested architectural improvements to enable better testability
- Private functions/methods that cannot be exercised via public API and analysis of why
- Estimated complexity and implementation priority
- Any potential challenges or special considerations
