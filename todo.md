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
- Add indicator for original newline type to `Content-Type` header.

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
- Support splitting large changes:
  - Multi-part mimeograms
  - Dependency tracking
  - Order preservation

## Usability Improvements

### Diff Enhancements
- Add support for colored output in terminals
- Implement file read caching to reduce I/O
- Add option to always show diff before apply
- Support hunk-by-hunk application of changes
- Allow use of external diff tools
- Support different diff formats

### Input/UX Improvements
- Support single-key actions without requiring Enter
- Improve terminal I/O handling
- Consider compound actions (e.g., edit-then-apply)
- Support restoring original content after edits
- Add progress indicators for long operations
- Support batch operations:
  - Queue all changes for review
  - Async fanout for applying changes
  - Progress tracking

### Configuration System
- Support environment variables for configuration
- Make protected paths configurable
- Special handling for XDG directories
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

### Security
- Implement robust path protection
- Add safeguards against symlink attacks
- Verify file ownership and permissions
- Support for checksums/signatures
- Handle file lock security implications

## Performance

### Optimization
- Optimize file I/O with caching
- Improve memory usage for large files
- Batch operations where possible
- Profile and optimize common operations
- Optimize async fanout for batch operations

# Notes

- Priority is given to stability and correctness
- New features should maintain the simple, composable design
- All features should work across platforms
- User experience should remain consistent and intuitive
- File format changes should be backward compatible

# Release 1.0 Checklist

[X] Represent original newline marker for textual `Content-Type`.
[X] Ensure correct charset and newlines during applies.
[ ] Single keystroke actions. (I.e., no ENTER key to act.)
[ ] Ability to queue applies. (Hit IDE/LS with all changes at once.)
[ ] Ability to choose hunks to apply.
[ ] Protect against changes to unsafe paths + override mechanism.
[ ] Command to produce prompt to give to LLM.
[ ] Creation option to prepend prompt with Mimeogram instructions.
[ ] Build standalone executables (PyOxidizer or PyInstaller + StaticX).
[ ] Tests.
[ ] Documentation.
