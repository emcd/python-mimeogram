# Future Development Plans

## Core Functionality Enhancements

### Format Enhancements
- Add `Presentation-Format` header support:
  - `line-numbers`: Dictionary mapping line numbers to content
  - `plain`: Default format (current behavior)
- Add `Differences-Mode` header support:
  - `edits-by-line-number`: Line-based insertions, replacements, deletions
  - `edits-by-context`: Context-based insertions, replacements, deletions
  - `unified-diff`: Direct unified diff from LLM
  - `none`: Whole file updates

### Project Structure
- Extract line-edit operations into standalone package (shared with AI
  workbench)
- Add boilerplate handling:
  - Strip boilerplate when creating mimeograms
  - Insert boilerplate when applying mimeograms
  - Make patterns configurable

### Size and Token Management
- Add mimeogram size estimation:
  - Line counting
  - Token estimation
  - Size warnings

## Usability Improvements

### Diff Enhancements
- Add support for colored output in terminals
- Implement file read caching to reduce I/O
- Add option to always show diff before apply
- Allow use of external diff tools
- Support various diff formats

### Input/UX Improvements
- Consider compound actions (e.g., edit-then-apply)
- Support restoring original content after edits
- Add progress indicators for long operations
- Support batch operations:
  - Queue all changes for review
  - Async fanout for applying changes
  - Progress tracking

### Configuration System
- Support environment variables for configuration
- User-configurable default actions
- Configure boilerplate patterns

## Code Quality

### Documentation and Testing
- Add comprehensive type hints
- Improve error handling
- Add examples of common workflows
- Document integration patterns
- Add troubleshooting guide
- Add comprehensive test suite:
  - Unit tests for core functionality
  - Integration tests with examples
  - Test different platforms
  - Test file locking scenarios

## File System Integration

### Core Features
- Add awareness of common file locks
- Support for binary files (via external handlers)
- Batch mode for automated updates
- Support for file permissions and metadata
- Version control system integration
- Save/restore session state for long updates

## Performance

### Optimization
- Optimize file I/O with caching
- Improve memory usage for large files
- Batch operations where possible
- Profile and optimize common operations
- Optimize async fanout for batch operations

## Terminal UI Enhancements

### Display Features
- Add terminal capability detection:
  - ANSI color support
  - Unicode/emoji support
  - Terminal width detection
- Add configurable color themes:
  - Protection status indicators
  - Diff highlighting
  - File information
  - Action menus
- Support status indicators:
  - File existence/permissions
  - Edit status tracking
  - Protection status with emoji
  - VCS status integration

### Progress Feedback
- Add operation progress indicators:
  - File processing status
  - Batch operation progress
  - Background task status
- Enhance error presentation:
  - Detailed error context
  - Recovery suggestions
  - Error highlighting
- Support status messages:
  - Operation success/failure
  - Warning notifications
  - Background task updates

## Path Protection

### Path Protection Enhancements
- Optimize path verification:
  - Add trie-like structure for path matching
  - Implement LRU cache for path expansions
  - Add separate caches for absolute and pattern-based rules
  - Consider stat cache for high-frequency checks
- Enhance WSL/MinGW support:
  - Improve path detection and translation
  - Handle custom mount points
  - Support non-standard WSL configurations
- Add configuration features:
  - Per-directory protection rules
  - Custom protection reason definitions
  - Path pattern exclusions

### Performance Improvements
- Cache expansions of home and environment variables
- Optimize pattern matching for frequently checked paths
- Cache directory traversal results
- Implement pattern matching short-circuits
- Add benchmarking for protection checks

### Usability Enhancements
- Improve protection reason messages
- Add detailed logging for protection decisions
- Documentation for common protection scenarios

### Testing and Validation
- Add comprehensive test suite for protection rules
- Create test mimeograms for various scenarios:
  - System directory access
  - Hidden file operations
  - Configuration directory writes
  - WSL/MinGW paths
  - Pattern-based protections
- Add protection rule validation

## Diff Enhancements

- Add side-by-side diff display with system compatibility:
  - Terminal width detection
  - Windows/Unix compatibility
  - Fallback for narrow terminals
- Support additional display options:
  - Color schemes with Pygments integration
  - Emoji markers for colorblind-friendly display
  - Whitespace visualization
  - Line wrapping and truncation
- Add content validation:
  - Binary content detection
  - Line length limits
  - Change count thresholds
  - Memory usage monitoring

## LLM Prompt Features

### Core Functionality
- Add library of standard prompts for different LLM capabilities:
  - Basic prompt (current) for high-capability models
  - Simplified prompt for models needing more explicit guidance
  - Detailed prompt for models requiring step-by-step instructions
- Support user-provided prompt overrides in config directory
- Consider environment variable to select prompt variant

### Testing Requirements

#### Prompt Command Tests
- Basic prompt display
  - Verify stdout contains exact prompt text
  - Ensure no additional whitespace/formatting changes
  - Check preservation of newlines and special characters
- Clipboard functionality
  - Verify prompt text is copied to clipboard unchanged
  - Test clipboard operations on various platforms
  - Handle clipboard access failures gracefully
- Error conditions
  - Test missing prompt file
  - Test inaccessible prompt file
  - Verify appropriate error messages and exit codes

#### Create Command Prompt Tests
- Basic functionality
  - Verify --prepend-prompt adds prompt correctly
  - Check prompt appears before any message
  - Ensure double newline between prompt and message
  - Verify mimeogram structure remains valid
- Combined operations
  - Test --prepend-prompt with --edit
  - Test --prepend-prompt with --clip
  - Verify all combinations of options work correctly
- Content integrity
  - Ensure file contents remain unchanged
  - Verify boundary markers are correct
  - Check Content-Type headers are preserved
  - Validate Content-Location headers
- Error handling
  - Test prompt file access failures during create
  - Verify error messages match project style
  - Check error propagation in combined operations

#### Integration Tests
- System tests with actual files
- Cross-platform verification (Windows/Unix)
- Large file handling

### Documentation
- Add prompt features to README.rst
- Document prompt variants when implemented
- Include common usage patterns and examples
- Document any configuration options added

# Notes

- Priority is given to stability and correctness
- New features should maintain the simple, composable design
- All features should work across platforms
- User experience should remain consistent and intuitive
- File format changes should be backward compatible

# Release 1.0 Checklist

[X] Represent original newline marker for textual `Content-Type`.
[X] Ensure correct charset and newlines during applies.
[X] Single keystroke actions. (I.e., no ENTER key to act.)
[ ] Ability to queue applies. (Hit IDE/LS with all changes at once.)
[X] Ability to choose hunks to apply.
[X] Protect against changes to unsafe paths + override mechanism.
[X] Command to produce prompt to give to LLM.
[X] Creation option to prepend prompt with Mimeogram instructions.
[ ] Build standalone executables (PyOxidizer or PyInstaller + StaticX).
[ ] Tests.
[ ] Documentation.
