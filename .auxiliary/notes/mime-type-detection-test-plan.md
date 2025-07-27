# MIME Type Detection Enhancement Test Plan

## Overview
Test plan for the comprehensive MIME type detection improvements that add pattern-based detection, charset-based fallback with content validation, and security hardening.

## Test Augmentations for Existing Test Blocks

### Block 400-499: MIME Type Tests (Augment existing test_400_detect_mime_types)

**Add to existing test_400_detect_mime_types:**
- Files with `+xml` suffixes: `.rs` files (application/rls-services+xml), custom XML formats
- Files with `+json` suffixes: HAL+JSON, JSON-LD formats  
- Files with `+yaml` suffixes: Docker Compose, Kubernetes manifests
- Files with `+toml` suffixes: Cargo.toml, pyproject.toml formats
- Verify these are accepted via pattern matching (not charset fallback)

**New test_4XX_application_x_security:**
- Test that binary `application/x-` types are properly rejected:
  - `.exe` files → `application/x-msdos-program` → should be REJECTED
  - `.iso` files → `application/x-iso9660-image` → should be REJECTED  
  - `.dmg` files → `application/x-apple-diskimage` → should be REJECTED
- Test that safe scripting `application/x-` types are accepted:
  - `.rb` files → `application/x-ruby` → should be ACCEPTED
  - `.py` files → `application/x-python` → should be ACCEPTED
  - `.pl` files → `application/x-perl` → should be ACCEPTED
- Test that unknown `application/x-` types fall through to charset testing

### Block 500-599: Error Handling Tests (Augment existing tests)

**Augment existing test_520_nontextual_mime:**
- Add test cases for binary files that have detectable charsets but fail content validation
- Test UTF-16LE false positives (repetitive binary data that decodes successfully)
- Verify appropriate warning messages are emitted

**New test_5XX_charset_fallback_validation:**
- Unknown MIME type + valid charset + reasonable content → should ACCEPT with debug message
- Unknown MIME type + valid charset + unreasonable content → should REJECT with warning  
- Unknown MIME type + charset decode failure → should REJECT with warning
- Test the specific content validation heuristics:
  - Single character repetition: `"aaaaaaa..."` → should REJECT
  - High control character ratio: mixed `\x00-\x1F` → should REJECT
  - Low printable character ratio: mostly binary → should REJECT
  - Valid code with symbols: `"fn main() { ... }"` → should ACCEPT

### Block 300-399: Character Set Tests (Augment existing test_300_detect_charset)

**Augment existing test_300_detect_charset:**
- Add test cases where charset is detected but content validation fails
- Test edge cases like:
  - Empty files with detected charset
  - Whitespace-only files  
  - Unicode content with various encodings
  - Mixed encoding artifacts

### Regression Test for Original Issue

**Add to appropriate existing block:**
- **test_4XX_rust_files_regression:** Specifically test that `.rs` files are now accepted without warnings
- Test various Rust code patterns to ensure robust handling
- Verify the exact scenario from the original bug report works correctly

## Content Validation Unit Tests

**New low-level tests for `_is_reasonable_text_content()` function:**
- Test boundary conditions for control character ratios
- Test boundary conditions for printable character ratios  
- Test various programming language syntaxes
- Test Unicode edge cases
- Test pathological inputs that should be rejected

## Integration Tests

**Add to existing integration test blocks:**
- Test end-to-end flow: unknown MIME type → charset detection → content validation → acceptance/rejection
- Test that debug and warning messages are emitted appropriately
- Test performance impact of content validation on large files
- Test interaction between pattern-based detection and charset fallback

## Test Data Requirements

**Files to create for testing:**
- Sample `.rs` files with various Rust syntax patterns
- Fake binary files with detectable charsets but invalid content
- Files with various `+xml`, `+json`, `+yaml`, `+toml` suffixes
- Scripting files for safe `application/x-` types
- Binary executables for dangerous `application/x-` types
- Edge case content files (high control chars, low printable ratio, etc.)

## Testing Priorities

1. **High Priority:** Security regression tests (binary file rejection)
2. **High Priority:** Original issue regression test (Rust files acceptance) 
3. **Medium Priority:** Content validation heuristics coverage
4. **Medium Priority:** Pattern-based detection coverage
5. **Low Priority:** Edge case and performance testing

## Notes

- All new tests should integrate into existing test block numbering
- Focus on augmenting existing tests where logical
- Ensure both strict and non-strict modes are tested for new functionality
- Verify appropriate log messages (debug/warning) are emitted
- Test both file system and HTTP acquisition paths where applicable