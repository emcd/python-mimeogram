# Mimeograms

In this conversation, we will use **mimeograms** for exchanging collections of
text files from a hierarchical directory structure or disparate sources. Below
are instructions on how to understand and process mimeograms.

## Format Specification

### Structure
- A mimeogram consists of one or more parts separated by boundary markers
- Each part contains headers followed by content
- Parts are separated by boundary lines starting with `--`
- The final boundary line ends with `--`

### Boundary Markers
- Format: `--====MIMEOGRAM_{uuid}====`
- Example: `--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====`
- The last boundary includes trailing dashes: `--====MIMEOGRAM_083f1e1306624ef4a246c23193d3fdd7====--`

### Headers
Each part must include:
1. `Content-Location`:
   - For messages: `mimeogram://editor-message`
   - For files: filesystem path or URL
2. `Content-Type`: MIME type and charset
   - Example: `Content-Type: text/x-python; charset=utf-8`

### Content
- Follows headers after a blank line
- Uses UTF-8 encoding
- No escaping or encoding of content (raw text)
- Preserves original line endings

## Interpretation Guidelines

### Editor Messages
- Parts with `Content-Location: mimeogram://editor-message` contain human messages
- These messages provide context about the other parts
- Messages should be interpreted as instructions or explanations

### File Parts
- Represent text files from a filesystem or URL
- Content-Location paths may be:
  - Relative paths (e.g., `src/main.py`)
  - Absolute paths (e.g., `/home/user/project/main.py`)
  - URLs (e.g., `https://example.com/file.txt`)
- Paths maintain their hierarchy even in the flat bundle format

### Processing Multiple Parts
- All parts in a bundle are related and should be processed together
- Order of parts may be significant
- Changes to one file may affect interpretation of others

## Common Use Cases

### Code Review and Modification
- Examine all file parts to understand the codebase structure
- Consider relationships between files (imports, dependencies)
- Maintain consistent style across modifications
- Respect project conventions visible in the files

### Design Discussions
- Read editor message for context about design decisions
- Reference specific files/lines when discussing changes
- Consider implications across all included files

### Project Organization
- Use paths to understand project structure
- Respect established module organization
- Maintain hierarchical relationships when suggesting changes

## Example

```
--====MIMEOGRAM_123456====
Content-Location: mimeogram://editor-message
Content-Type: text/plain; charset=utf-8

Please review these Python modules for a logging system.
--====MIMEOGRAM_123456====
Content-Location: src/logger.py
Content-Type: text/x-python; charset=utf-8

class Logger:
    def __init__(self):
        pass
--====MIMEOGRAM_123456====--
```

In this example:
1. The message part provides context about the purpose
2. The file part shows a Python module to be reviewed
3. The relative path `src/logger.py` indicates project structure

## Processing Instructions

When working with mimeograms:
1. Read the editor message first to understand context
2. Examine file paths to understand project structure
3. Process all parts as a cohesive unit
4. Maintain the same format when responding with file changes
5. Preserve original paths unless explicitly asked to change them

Remember that mimeograms are designed to facilitate structured discussion about
code and project organization while maintaining context across multiple files.
