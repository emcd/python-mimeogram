# Mimeograms

In this conversation, we will use **mimeograms** for exchanging collections of
text files from a hierarchical directory structure or disparate sources. Below
are instructions on how to understand and process mimeograms.

## Format Specification

### Structure
- A mimeogram consists of one or more parts separated by boundary markers.
- Each part contains headers followed by content.
- Parts are separated by boundary lines starting with `--`.
- The final boundary line ends with `--`.

### Boundary Markers
- Format: `--====MIMEOGRAM_{uuid}====`
- Example: `--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====`
- The last boundary includes trailing dashes: `--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====--`

### Headers
Each part must include:
1. `Content-Location`:
   - For optional messages: `mimeogram://message`
   - For files: original filesystem path or URL
2. `Content-Type`: Original MIME type, charset, and newline marker
   - Example: `Content-Type: text/x-python; charset=utf-8; linesep=LF`

### Content
- Follows headers after a blank line.
- Normalized to UTF-8 character set.
- Normalized to Unix (LF) line endings.

## Interpretation Guidelines

### Messages
- Parts with `Content-Location: mimeogram://message` contain human messages.
- These messages provide context about the other parts or may be a general
  response to a previous assistant turn.

### File Parts
- Represent text files from a filesystem or URL.
- Content-Location paths may be:
  - Relative paths (e.g., `src/main.py`)
  - Absolute paths (e.g., `/home/user/project/main.py`)
  - URLs (e.g., `https://example.com/file.txt`)
- Paths maintain their hierarchy even in the flat bundle format.

## Common Use Cases

### Code Review and Modification
- Examine all file parts to understand the codebase structure.
- Consider relationships between files (imports, dependencies).
- Maintain consistent style across modifications.
- Respect project conventions visible in the files.

### Design Discussions
- Read message for context about design decisions.
- Reference specific files/lines when discussing changes.
- Consider implications across all included files.

### Project Organization
- Use paths to understand project structure.
- Respect established module organization.
- Maintain hierarchical relationships when suggesting changes.

## Example

```
--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====
Content-Location: mimeogram://message
Content-Type: text/plain; charset=utf-8; linesep=LF

Please review these Python modules for a logging system.
--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====
Content-Location: src/logger.py
Content-Type: text/x-python; charset=utf-8; linesep=LF

class Logger:
    def __init__(self):
        pass
--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====--
```

In this example:
1. The message part provides context about the purpose.
2. The file part shows a Python module to be reviewed.
3. The relative path `src/logger.py` indicates project structure.

## Processing Instructions

When working with mimeograms:
1. Read the message first to understand context.
2. Examine file paths to understand project structure.
3. Maintain the same format when responding with file changes.
4. Preserve original paths unless explicitly asked to change them.
