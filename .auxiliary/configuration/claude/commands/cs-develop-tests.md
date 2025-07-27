---
allowed-tools: Bash(hatch --env develop run:*), Bash(git status), Bash(git log:*), Bash(echo:*), Bash(ls:*), Bash(find:*), LS, Read, Glob, Grep, Write, Edit, MultiEdit, WebFetch
description: Implement comprehensive tests following an existing test plan and project guidelines
---

# Implement Tests

**NOTE: This is an experimental workflow! If anything seems unclear or missing,
please stop for consultation with the user.**

For systematic test implementation following a pre-created test plan and project testing guidelines.

Test plan path: `$ARGUMENTS`

**CRITICAL**: Implement tests according to the provided test plan only.
**HALT if**:
- No test plan path is provided
- Test plan cannot be read or is invalid
- Plan conflicts with project testing principles
- Implementation deviates from plan without justification

## Context

- Current git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Test plan to implement: !`ls "$ARGUMENTS" 2>/dev/null && echo "Present" || echo "Missing - HALT"`
- Existing test structure: !`find tests -name "*.py" | head -20`
- Test README: !`ls tests/README.md 2>/dev/null && echo "Present" || echo "Missing"`

## Prerequisites

Ensure that you:
- Have a valid test plan document
- Have verified access to target code modules referenced in the plan
- Have read any relevant `CLAUDE.md` file
- Understand the [test-writing guidelines](https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst)

## Testing Principles (from project guidelines)

**Core Principles:**
1. **Dependency Injection Over Monkey-Patching**: Use injectable dependencies
   for testability
2. **Performance-Conscious**: Prefer in-memory filesystems (pyfakefs) over temp
   directories
3. **Avoid Monkey-Patching**: Never patch internal code; use dependency
   injection instead
4. **100% Coverage Goal**: Aim for complete line and branch coverage
5. **Test Behavior, Not Implementation**: Focus on observable behavior and
   contracts

**Anti-Patterns to Avoid:**
- Monkey-patching internal code (will fail with immutable objects)
- Excessive mocking of internal components
- Testing implementation details vs. behavior
- Using temp directories when pyfakefs suffices

**Organization:**
- Follow the systematic numbering conventions detailed in the test guidelines

## Safety Requirements

**CRITICAL**: You MUST halt the process and consult with the user if ANY of the
following occur:

- **Plan Deviation**: If implementation cannot follow the test plan as specified
- **Anti-Pattern Detection**: If plan requires tests that violate project principles
- **Architecture Conflicts**: If tests require monkey-patching internal code
- **Numbering Conflicts**: If planned test numbering clashes with existing conventions
- **Missing Dependencies**: If required test fixtures or dependencies are unavailable
- **Plan Inconsistencies**: If the test plan contains contradictions or unclear instructions

**Your responsibilities:**
- Follow the test plan precisely while adhering to project conventions
- Use dependency injection patterns as specified in the plan
- Implement tests exactly as planned without adding extras
- Maintain systematic test numbering as outlined in the plan
- Ensure tests validate behavior, not implementation
- Document any necessary deviations from the plan with clear justification

## Test Implementation Process

Execute the following steps for test plan: `$ARGUMENTS`

### 0. Pre-Flight Verification
**MANDATORY - Verify access to project guidelines:**

Use WebFetch to access and confirm you can read the complete project guidelines:
- Testing: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst
- Practices: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst
- Style: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/style.rst

**CRITICAL**: You MUST successfully access and read all three guides before
proceeding. If WebFetch fails for any guide, HALT and consult with the user.

### 1. Test Plan Reading and Validation
**CRITICAL - Read and validate the provided test plan:**

Read the test plan document at the provided path:
```
Read the test plan file at: $ARGUMENTS
```

**Validate plan completeness:**
- Verify plan contains coverage analysis summary
- Confirm test strategy is clearly defined
- Check that component-specific tests are detailed
- Ensure implementation notes are present
- Validate success metrics are specified

**HALT if the plan is incomplete, unclear, or missing critical sections.**

### 2. Plan Compliance Verification
**Ensure plan aligns with project principles:**

**Verify plan adheres to project testing guidelines:**
- No monkey-patching of internal code required
- Dependency injection patterns are viable
- Test numbering follows project conventions
- No external network testing planned

**Check for conflicts with existing tests:**
- Review planned test module names against existing files
- Verify planned test function numbering doesn't conflict
- Ensure no duplication of existing test coverage

### 3. Test Data and Fixture Setup
**Prepare test data as specified in the plan:**

**Create required test data under tests/data/:**
- Set up fake packages for extension mechanisms (if planned)
- Prepare captured artifacts and snapshots (if planned)
- Create any mock data files as specified in the plan

**CRITICAL**: Only create test data explicitly mentioned in the test plan.

### 4. Test Module Creation/Updates
**Implement test modules following the plan:**

**For each planned test module:**
- Create or update test files with planned naming (e.g., `test_100_exceptions.py`)
- Follow planned test function numbering within modules
- Implement only the tests specified in the plan
- Use dependency injection patterns as outlined in the plan

**Key Implementation Guidelines:**
- Use dependency injection for all external dependencies as planned
- Prefer `pyfakefs.Patcher()` for filesystem operations as specified
- Mock only third-party services, never internal code
- **Insert tests in numerical order within files** - do NOT append to end
- **Write behavior-focused docstrings**: "Functionality is correct with Y" NOT "function_name does X with Y"
- Follow existing naming conventions and code style
- Implement tests in the exact order and numbering specified in the plan

### 5. Coverage Validation
**Verify implementation matches plan coverage goals:**
```bash
hatch --env develop run testers
hatch --env develop run coverage report --show-missing
```

**CRITICAL - VERIFY PLAN COMPLIANCE:**
- Run full test suite to ensure no regressions
- Check that coverage matches the plan's target metrics
- Verify all planned test functions are implemented
- Confirm coverage gaps identified in the plan are addressed
- Ensure no existing functionality is broken

### 6. Code Quality Validation
**Ensure implemented tests meet project standards:**
```bash
hatch --env develop run linters
```

**Requirements:**
- All linting checks must pass
- Note that the linters do not check style; you must verify style compliance
- No violations of project coding standards
- Test docstrings are clear and descriptive
- Proper imports and dependencies
- Implementation follows all conventions specified in the plan

## Test Pattern Examples

**Dependency Injection Pattern:**
```python
async def test_100_process_with_custom_processor( ):
    ''' Process function accepts custom processor via injection. '''
    def mock_processor( data ):
        return f"processed: {data}"

    result = await process_data( 'test', processor = mock_processor )
    assert result == "processed: test"
```

**Filesystem Operations (Preferred):**
```python
def test_200_config_file_processing( ):
    ''' Configuration files are processed correctly. '''
    with Patcher( ) as patcher:
        fs = patcher.fs
        fs.create_file( '/fake/config.toml', contents = '[section]\nkey="value"' )
        result = process_config_file( Path( '/fake/config.toml' ) )
        assert result.key == 'value'
```

**Error Handling:**
```python
def test_300_invalid_input_handling( ):
    ''' Invalid input raises appropriate exceptions. '''
    with pytest.raises( ValueError, match = "Invalid data format" ):
        process_invalid_data( "malformed" )
```

## Success Criteria

Implementation is complete when:
- [ ] All tests specified in the plan have been implemented
- [ ] Coverage matches or exceeds the plan's target metrics
- [ ] All planned test modules and functions are created with correct numbering
- [ ] Test data and fixtures are set up as specified in the plan
- [ ] All new tests pass consistently
- [ ] No existing tests are broken
- [ ] Linting passes without issues
- [ ] Project coding practices and style have been followed
- [ ] Tests follow project numbering conventions as planned
- [ ] Tests are inserted in proper numerical order within files
- [ ] Test docstrings focus on behavior, not function names
- [ ] Dependency injection is used as specified in the plan
- [ ] No monkey-patching of internal code
- [ ] Performance-conscious patterns are applied as planned

**Note**: Always run full validation (`hatch --env develop run linters && hatch
--env develop run testers`) before considering the task complete.

## Final Report

Upon completion, provide a brief report covering:
- **Plan Compliance**: Confirmation that all planned tests were implemented as specified
- **Coverage Achievement**: Final coverage percentages vs. plan targets
- **Deviations from Plan**: Any necessary changes made to the plan during implementation with justification
- **Technical Issues Resolved**: Any conflicts encountered and how they were resolved
- **Pragma Directives Applied**: Any `# pragma: no cover` or `# pragma: no branch` added with rationale
- **Test Data Created**: Summary of fixtures and test data files created under `tests/data/`
- **Module Updates**: List of test modules created or updated with their numbering
- **Code Quality**: Confirmation that tests are properly ordered and have behavior-focused docstrings
