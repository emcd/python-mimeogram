# create-mimeogram

## Purpose
Enables users to bundle multiple files and directories into a single, structured document (a "mimeogram") suitable for sharing with Large Language Models (LLMs). This capability preserves file metadata and directory structure, facilitating code reviews and project sharing.

## Requirements

### Requirement: Source Acquisition
The system SHALL accept one or more source locations to include in the mimeogram.

Priority: Critical

#### Scenario: File inputs
- **WHEN** user provides a list of file paths
- **THEN** the content of each file is included in the mimeogram

#### Scenario: Directory inputs
- **WHEN** user provides a directory path
- **AND** recursion is enabled (or default behavior)
- **THEN** files within that directory are included

#### Scenario: URL inputs
- **WHEN** user provides a URL
- **THEN** the content at that URL is fetched and included

### Requirement: Recursion Control
The system SHALL allow users to control whether directory traversal is recursive.

Priority: Medium

#### Scenario: Recursive traversal
- **WHEN** user enables recursion (explicitly or by default)
- **THEN** subdirectories are traversed and their files included

#### Scenario: Non-recursive traversal
- **WHEN** user disables recursion
- **THEN** only files in the immediate directory are included

### Requirement: Exclusion Filtering
The system SHALL exclude files based on ignore rules (e.g., `.gitignore`) by default, but allow disabling this filtering.

Priority: High

#### Scenario: Default exclusion
- **WHEN** user creates a mimeogram in a git repository
- **THEN** files listed in `.gitignore` are excluded

#### Scenario: Disable exclusion
- **WHEN** user provides the `--no-ignores` flag
- **THEN** files listed in `.gitignore` are included

### Requirement: Clipboard Output
The system SHALL provide an option to copy the generated mimeogram directly to the system clipboard.

Priority: High

#### Scenario: Copy to clipboard
- **WHEN** user provides the `--clipboard` flag
- **THEN** the mimeogram is copied to the clipboard
- **AND** a success message is displayed

### Requirement: Token Counting
The system SHALL provide an option to count and display the number of tokens in the generated mimeogram.

Priority: Medium

#### Scenario: Count tokens
- **WHEN** user provides the `--count-tokens` flag
- **THEN** the total token count is calculated using the configured tokenizer
- **AND** the count is displayed to the user

### Requirement: Introductory Message
The system SHALL allow users to add an introductory message to the mimeogram, optionally launching an editor to capture it.

Priority: Low

#### Scenario: Edit message
- **WHEN** user provides the `--edit-message` flag
- **THEN** the system default editor is launched
- **AND** the user's saved text is included as a message in the mimeogram

### Requirement: Prompt Prepending
The system SHALL allow users to prepend standard mimeogram format instructions to the output.

Priority: Medium

#### Scenario: Prepend prompt
- **WHEN** user provides the `--prepend-prompt` flag
- **THEN** the standard mimeogram instructions are added to the beginning of the output

### Requirement: Strict Mode
The system SHALL allow users to control behavior when encountering invalid or inaccessible files.

Priority: Low

#### Scenario: Strict mode enabled
- **WHEN** user provides the `--fail-on-invalid` flag
- **AND** a source file is inaccessible
- **THEN** the process fails with an error

#### Scenario: Strict mode disabled (default)
- **WHEN** strict mode is not enabled
- **AND** a source file is inaccessible
- **THEN** the file is skipped and a warning is logged

### Requirement: Deterministic Output
The system SHALL allow users to generate reproducible mimeograms with deterministic boundary markers.

Priority: Low

#### Scenario: Deterministic boundary
- **WHEN** user provides the `--deterministic-boundary` flag
- **THEN** the MIME boundary is generated based on content hash
