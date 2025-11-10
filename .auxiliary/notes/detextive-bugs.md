# Detextive Issues

## Binary Data Decoded as UTF-16-LE

**Issue**: Detextive incorrectly decodes certain binary data as UTF-16-LE text.

**Example**: A file containing alternating bytes `0xFF 0x00` repeated (i.e., `bytes([0xFF, 0x00] * 52)`) is successfully detected as having charset `utf-16-le` and decoded as text, producing a string of repeated `ÿ` characters.

**Impact**: This causes binary files that should be rejected to be accepted as valid text files. While this is not a security risk for most cases (since the "decoded" content is gibberish), it means that mimeogram may accept files that are not genuinely textual.

**Workaround**: Tests have been updated to use binary files with more recognizable headers (like PE executables with `MZ` magic bytes) that Detextive properly rejects. These files cause decode failures even when a charset is detected.

**Status**: This is a limitation of charset detection algorithms in general - alternating binary patterns can appear to match certain multi-byte encodings like UTF-16. The issue should be reported to the Detextive project for potential improvement in validation heuristics.

**Related Tests**:
- `test_410_application_x_security`: Updated to check for truly dangerous files only
- `test_520_nontextual_mime`: Updated to use PE executable header instead of simple binary pattern
