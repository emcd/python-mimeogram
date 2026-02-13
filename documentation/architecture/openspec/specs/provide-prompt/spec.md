# provide-prompt

## Purpose
Provides users with the standard prompt text used to instruct LLMs on the mimeogram format. This facilitates manual copy-pasting or integration into LLM project instructions.

## Requirements

### Requirement: Prompt Output
The system SHALL output the standard mimeogram prompt text.

Priority: High

#### Scenario: Output to stdout
- **WHEN** user executes the command
- **THEN** the prompt text is printed to standard output

### Requirement: Clipboard Copy
The system SHALL provide an option to copy the prompt text directly to the clipboard.

Priority: Medium

#### Scenario: Copy to clipboard
- **WHEN** user provides the `--to-clipboard` flag
- **THEN** the prompt text is copied to the system clipboard
- **AND** a success message is displayed
