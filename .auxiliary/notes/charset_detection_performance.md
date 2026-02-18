# Charset Detection Performance Issue

## Problem

`mimeogram create` takes ~49 seconds when processing large binary files (e.g., 17MB ELF executable).

## Investigation

### Test Case
- File: `.auxiliary/artifacts/pyinstaller/mimeogram`
- Type: ELF 64-bit executable (binary)
- Size: 16.34 MB

### Performance Breakdown

| Operation | Time | Notes |
|-----------|------|-------|
| Read 17MB file | 0.008s | File I/O is not the issue |
| chardet (full file) | 47.876s | **THE BOTTLENECK** |
| charset-normalizer (full file) | 0.659s | 77x faster than chardet |
| chardet (8KB chunk) | 0.012s | 4000x faster than full file |

### Root Cause

**chardet** has O(n) or worse complexity when analyzing file contents. The detextive library defaults to trying chardet first:

```python
charset_detectors_order=('chardet', 'charset-normalizer')
```

For large binary files:
1. chardet analyzes entire 17MB → 48 seconds → returns `None` (correct)
2. charset-normalizer not tried (chardet already returned a result)

## Results Comparison

**Full 17MB binary file:**
- chardet: `{'encoding': None, 'confidence': 0.0}` (correct, but slow)
- charset-normalizer: `None` (correct, fast)

**First 8KB chunk:**
- chardet: `{'encoding': 'MacRoman', 'confidence': 0.54}` (false positive, but fast)

## Potential Solutions

### Option 1: Chunk-based Detection
**Approach**: Only pass first 8-32KB to detextive for charset detection.

**Pros**:
- 4000x faster (0.012s vs 48s)
- Simple implementation
- Works for most text files (headers are usually at the top)

**Cons**:
- May misidentify binary files as text (false positive: MacRoman at 54% confidence)
- Could miss charset declarations in large files

**Risk**: False positives could cause issues downstream

### Option 2: Reorder Charset Detectors
**Approach**: Configure detextive to try charset-normalizer before chardet.

**Pros**:
- 77x faster (0.66s vs 48s)
- Still analyzes full file (more accurate)
- Simple configuration change
- No risk of false positives

**Cons**:
- Still ~0.7s per large binary (slower than chunk-based)
- Doesn't solve fundamental O(n) issue

**Implementation**:
```python
behaviors = __.detextive.core.Behaviors(
    charset_detectors_order=('charset-normalizer', 'chardet')
)
mimetype, charset = __.detextive.infer_mimetype_charset(
    content, location=str(location), behaviors=behaviors
)
```

### Option 3: MIME Type First Detection
**Approach**: Use libmagic/file to detect binary files before charset detection.

**Pros**:
- Can short-circuit charset detection entirely for known binary types
- Very fast for binaries
- Most accurate

**Cons**:
- More complex implementation
- Requires understanding detextive's mimetype detection flow
- May need to call detection twice (once for mimetype, once for charset)

**Note**: detextive already uses libmagic via `mimetype_detectors_order=('magic', 'puremagic')`, but the current code flow doesn't use this to skip charset detection.

### Option 4: Size Threshold
**Approach**: Skip charset detection for files above a certain size (e.g., 10MB).

**Pros**:
- Simple implementation
- Protects against pathological cases

**Cons**:
- Arbitrary threshold
- Doesn't help with 1-10MB binaries
- May reject legitimate large text files

### Option 5: Upstream Fix
**Approach**: Contribute to detextive to add a `max_bytes` parameter.

**Pros**:
- Proper solution that helps entire ecosystem
- Maintains accuracy while improving performance

**Cons**:
- Takes time for upstream acceptance and release
- Need to maintain workaround in meantime

## Recommendation

**Short term**: Option 2 (Reorder detectors)
- Immediate 77x speedup
- No risk of false positives
- One-line configuration change

**Medium term**: Option 3 (MIME type first)
- Investigate detextive's mimetype detection to avoid charset detection for binaries
- Requires understanding the internal flow better

**Long term**: Option 5 (Upstream contribution)
- Add `max_bytes` parameter to detextive
- Or improve chardet performance for binary data

## Code Location

The charset detection happens in `sources/mimeogram/acquirers.py`:

```python
async def _acquire_from_file( location: __.Path ) -> _parts.Part:
    # Line 83-84:
    mimetype, charset = __.detextive.infer_mimetype_charset(
        content_bytes, location = str( location ) )
```

And similarly in `_acquire_via_http` (lines 115-118).
