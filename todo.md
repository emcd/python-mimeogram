# Future Development Plans

## Format Enhancements
- Add `Presentation-Format` header support:
  - `line-numbers`: Dictionary mapping line numbers to content
  - `plain`: Default format (current behavior)
- Add `Differences-Mode` header support:
  - `edits-by-line-number`: Line-based insertions, replacements, deletions
  - `edits-by-context`: Context-based insertions, replacements, deletions
  - `unified-diff`: Direct unified diff from LLM
  - `none`: Whole file updates
- Consider extracting line-edit operations into standalone package (shared with AI workbench)
- Add boilerplate handling:
  - Strip boilerplate when creating mimeograms
  - Insert boilerplate when applying mimeograms
  - Make patterns configurable

## Diff Enhancements
- Add support for colored output in terminals
- Implement file read caching to reduce I/O
- Add option to always show diff before apply
- Support hunk-by-hunk application of changes
- Allow use of external diff tools
- Support different diff formats (unified, side-by-side)

## Input/UX Improvements
- Support single-key actions without requiring Enter
- Improve terminal I/O handling
- Consider compound actions (e.g., edit-then-apply)
- Support restoring original content after edits
- Add progress indicators for long operations
- Support batch operations:
  - Queue all changes for review
  - Async fanout for applying changes
  - Progress tracking for batch operations

## Configuration System
- Add configuration file support
- Support environment variables for configuration
- Make protected paths configurable
- Special handling for XDG directories
- User-configurable default actions
- Configure boilerplate patterns

## Code Quality
- Refactor code to minimize class sizes:
  - Move non-self-using methods to standalone functions
  - Consider functional core with OO shell
- Replace argparse with tyro:
  - Define command and options objects
  - Add default command support
  - Improve CLI ergonomics
- Add comprehensive type hints
- Improve error handling

## File System Integration
- Add awareness of common file locks
- Support for binary files (maybe via external handlers)
- Batch mode for automated updates
- Support for file permissions and metadata
- Version control system integration
- Save/restore session state for long updates

## Documentation
- Add examples of common workflows
- Provide configuration templates
- Document integration patterns with other tools
- Add troubleshooting guide
- Document new header types and formats
- Add examples of boilerplate configuration

## Testing
- Add comprehensive test suite
- Add integration tests with example files
- Test rollback functionality
- Test on different platforms and terminals
- Test with various editor configurations
- Test file locking scenarios
- Test batch operations

## Performance
- Optimize file I/O with caching
- Improve memory usage for large files
- Batch operations where possible
- Profile and optimize common operations
- Optimize async fanout for batch operations

## Security
- Implement robust path protection
- Add safeguards against symlink attacks
- Verify file ownership and permissions
- Support for checksums/signatures
- Handle file lock security implications

Notes:
- Priority is given to stability and correctness
- New features should maintain the simple, composable design
- All features should work across platforms
- User experience should remain consistent and intuitive
- File format changes should be backward compatible
