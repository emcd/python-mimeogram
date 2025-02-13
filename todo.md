# Development Roadmap

## 1. Core Functionality

### Content Processing
- Format Enhancements
  - Add `Presentation-Format` header (line-numbers, plain)
  - Add `Differences-Mode` header (line edits, context edits, unified diff)
  - Add boilerplate handling (strip/inject with configurable patterns)
- Size Management
  - Line and token counting
  - Size estimation and warnings
  - Memory usage monitoring

### Extensibility
- Plugin/Extension System
  - External diff tool support
  - Binary file handlers
  - Custom transformations
- Extract Reusable Components
  - Line-edit operations package
  - Path protection system

## 2. User Experience

### Interface Improvements
- Terminal Capabilities
  - Color and emoji support
  - Width detection and adaptation
  - Side-by-side diffs with fallbacks
- Progress Feedback
  - Operation status indicators
  - Batch operation progress
  - Background task status
- Enhanced Error Handling
  - Detailed error context
  - Recovery suggestions
  - Improved error messages

### Workflow Enhancements
- Compound Operations
  - Edit-then-apply actions
  - Batch operations with queuing
  - Async fanout for applies
- Content Management
  - File read caching
  - Session state save/restore
  - Original content restoration
- Configuration
  - Environment variable support
  - User-configurable defaults
  - Boilerplate patterns

## 3. System Integration

### File System
- Path Protection Improvements
  - Optimized path verification
  - Enhanced WSL/MinGW support
  - Per-directory rules
  - Pattern exclusions
- Resource Management
  - File lock awareness
  - Permission handling
  - Metadata preservation
- Version Control
  - VCS status integration
  - Change tracking

### Performance
- I/O Optimization
  - File operation caching
  - Directory traversal caching
  - Batch operations
- Memory Management
  - Large file handling
  - Resource pooling
  - Operation profiling

## 4. Distribution

### Standalone Executables
- Build System
  - Multi-platform arm64 support
  - PyOxidizer configuration
  - Size optimization
- Code Signing
  - macOS notarization
  - Windows signing
  - Distribution channels

### LLM Integration
- Prompt System
  - Standard prompt library
  - Capability-based variants
  - User overrides
  - Environment selection

## 5. Quality Assurance

### Testing
- Core Functionality
  - Unit tests
  - Integration tests
  - Platform verification
  - Resource handling
- Feature-Specific
  - Prompt system
  - Path protection
  - Standalone executables
  - Format changes

### Documentation
- User Guides
  - Installation and setup
  - Common workflows
  - Integration patterns
  - Troubleshooting
- Technical Reference
  - API documentation
  - Type hints
  - Configuration options
  - Release notes

## Implementation Guidelines
- Prioritize stability and correctness
- Maintain simple, composable design
- Ensure cross-platform compatibility
- Keep UX consistent and intuitive
- Preserve backward compatibility

## Release Checklist

✓ Newline preservation
✓ Charset handling
✓ Single keystroke actions
✓ Change queuing
✓ Hunk selection
✓ Path protection
✓ LLM prompt command
✓ Prompt prepending
✓ Standalone executables
✓ Testing
□ Documentation
