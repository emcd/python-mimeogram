---
allowed-tools: Bash(git status), Bash(git branch:*), Bash(git log:*), Bash(hatch version:*), Bash(echo:*), Bash(ls:*), Bash(pwd), LS, Read
description: Validate custom slash command functionality with context and permissions
---

# Validate Custom Slash Command

Test script to validate custom slash command functionality, permissions, and context interpolation.

Test argument: `$ARGUMENTS`

## Context

- Current directory: !`pwd`
- Current git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Current version: !`hatch version`
- Recent commits: !`git log --oneline -5`
- Template files: !`ls template/.auxiliary/configuration/claude/commands/`

## Validation Tasks

1. **Report the test argument**: Look at the "Test argument:" line above and tell me what value you see there
2. **Test basic git commands**: Run `git status` and `git branch --show-current`
3. **Test hatch command**: Run `hatch version`
4. **Test file operations**: Use LS tool to list current directory contents
5. **Test restricted command**: Attempt `git push` (should be blocked and require approval)

## Expected Results

- Context should be populated with current state
- Allowed commands should execute successfully
- `git push` should be blocked

## Your Task

Execute the validation tasks above and provide a summary report including:
- The interpolated argument value you see on the "Test argument:" line
- Results of each allowed command
- Confirmation that restricted commands are properly blocked
- Any observations about the command execution experience
