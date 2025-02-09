# Mimeogram Testing Progress and Plans

## Test Module Organization

### Current Structure
```
tests/
  test_000_mimeogram/       # Core package tests
    __init__.py            # Test utilities and constants
    conftest.py           # Shared test fixtures

    # Internal Modules Tests (mimeogram.__)
    test_010_base.py      # Basic package structure tests
    test_015_exceptions.py # Exception hierarchy tests
    test_020_generics.py  # Generic types tests
    test_025_dictedits.py # Dictionary editing tests
    test_030_asyncf.py    # Async utilities tests
    test_035_processes.py # Process management tests
    test_040_io.py       # File I/O operations tests
    test_045_inscription.py # Logging configuration tests
    test_050_application.py # Application metadata tests
    test_055_distribution.py # Distribution info tests
    test_060_state.py    # Global state management tests
    test_065_configuration.py # Config management tests
    test_070_environment.py # Environment variable handling tests
    test_075_preparation.py # Library initialization tests

    # Public API Tests
    # Foundation Layer (100-190)
    test_100_exceptions.py  # Exception hierarchy tests
    test_110_parts.py      # Core data structures tests

    # Parser/Formatter Layer (200-290)
    test_200_parsers.py    # Mimeogram parsing tests
    test_210_formatters.py # Mimeogram formatting tests

    # Utility Layer (300-390)
    test_300_display.py    # Display utilities tests
    test_310_edit.py       # Edit utilities tests
    test_320_differences.py # Difference handling tests
    test_330_interactions.py # User interactions tests

    # Filesystem Protection Layer (400-490)
    test_400_fsprotect_core.py    # Core protection types tests
    test_410_fsprotect_home.py    # Home directory protection tests
    test_420_fsprotect_project.py # Project directory protection tests
    test_430_fsprotect_platform.py # Platform-specific protection tests
    test_440_fsprotect_cache.py    # Protection rule caching tests

    # Content Handler Layer (500-590)
    test_500_acquirers.py  # Content acquisition tests
    test_510_updaters.py   # Content updates tests

    # CLI Layer (600-690)
    test_600_create.py     # Create command tests
    test_610_apply.py      # Apply command tests
    test_620_prompt.py     # Prompt command tests
    test_630_cli.py        # Command-line interface tests
```

### Completed Internal Modules (mimeogram.__)
- `exceptions.py`: Exception hierarchy and behaviors (100%)
- `generics.py`: Result type and variants (100%)
- `dictedits.py`: Dictionary editing functionality (100%)
- `asyncf.py`: Async utilities and error handling (100%)
- `processes.py`: Process management utilities (100%)
- `io.py`: File I/O operations (100%)
- `inscription.py`: Logging and debug printing configuration (100%)
- `application.py`: Application metadata handling (100%)
- `distribution.py`: Package distribution info (65% - PyOxidizer paths untested)
- `state.py`: Global state management (100%)
- `configuration.py`: Configuration management (100%)
- `environment.py`: Environment variable handling (100%)
- `preparation.py`: Library initialization (100%)

### Pending Internal Modules

All core internal modules have test coverage now, with the exception of some
PyOxidizer-specific code paths in distribution.py that would require a special
test environment.

## Planned Features

### Test Data Bank
Location: `tests/test_000_mimeogram/data/mimeograms/`

Structure:
```
mimeograms/
  valid/
    simple_text.mg
    mixed_content.mg
    utf8_content.mg
    empty_parts.mg
    max_headers.mg
  invalid/
    missing_boundary.mg
    invalid_headers.mg
    wrong_charset.mg
    truncated.mg
```

Helper function to implement:
```python
def acquire_test_mimeogram( name: str ) -> str:
    ''' Acquires test mimeogram from data directory.

    Args:
        name: Name of mimeogram file without extension
    '''
    from pathlib import Path
    test_dir = Path( __file__ ).parent
    location = test_dir / 'data' / 'mimeograms' / f"{name}.mg"
    return location.read_text( )
```

### Property-Based Testing
Tool: Hypothesis

Areas to cover:
1. Mimeogram format validation
   - Boundary generation
   - Header combinations
   - Content variations

2. Content processing
   - Character encodings
   - Line endings
   - Size variations

3. Error conditions
   - Malformed input
   - Edge cases
   - Recovery scenarios

## Infrastructure Improvements

### Noted Issues
1. `generics.Result` needs to be converted to proper ABC
2. Review class/instance attribute immutability in exceptions
3. Consider PyOxidizer-specific tests if needed for distribution.py

## Testing Strategy

### Core Modules
1. Test in dependency order
2. Focus on interface contracts
3. Ensure error handling coverage
4. Test immutability guarantees

### I/O and External Interactions
1. Use fixtures for filesystem isolation
2. Mock external services
3. Use pytest-httpx for HTTP testing
4. Handle async operations properly

### Integration Testing
1. Test full workflows
2. Verify component interactions
3. Test CLI interface
4. Ensure proper cleanup

## Next Steps

1. Immediate Tasks
   - Review test plan for public API modules
   - Start design of mimeogram test data bank
   - Consider scope of integration tests needed

2. Medium Term
   - Complete public API module tests
   - Set up test mimeogram bank
   - Add integration tests

3. Future Work
   - Consider PyOxidizer-specific testing strategy
   - Review and improve fixtures if needed
   - Implement property-based testing

## Notes
- Follow project style guidelines
- Use appropriate number ranges for different test module groups
- Maintain test independence
- Keep coverage at 100% where feasible
- Some modules like distribution.py may have lower coverage due to
  environment-specific code paths (e.g., PyOxidizer)
