.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
                             Tool Comparisons
*******************************************************************************

Overview of Tools
===============================================================================

Mimeogram
-------------------------------------------------------------------------------
- Emphasizes round-trip capability (create & apply changes)
- Focuses on structured, metadata-rich file bundling with format preservation
- Uses MIME-inspired format for robust metadata handling
- CLI-first with clipboard integration

Gitingest
-------------------------------------------------------------------------------
- Web-first approach with CLI/package options
- Browser extensions for all major browsers
- Smart URL-based access
- Token counting and statistics
- Both sync and async Python APIs
- Multiple browser extensions

Repomix
-------------------------------------------------------------------------------
- Emphasizes repository-level processing with multiple bundle formats
- Provides web interface and VS Code extension
- Focuses on security and token optimization

dump_dir
-------------------------------------------------------------------------------
- Optimized for speed and simplicity
- Direct clipboard integration
- Lightweight configuration via YAML

ai-digest
-------------------------------------------------------------------------------
- Simple Markdown-based output
- Supports custom ignore patterns
- Minimal configuration required
- Focus on whitespace optimization

Feature Comparison
===============================================================================

Core Features
-------------------------------------------------------------------------------

+--------------------+------------+------------+-------------+------------+------------+
| Feature            | Mimeogram  | Gitingest  | Repomix     | dump_dir   | ai-digest  |
+====================+============+============+=============+============+============+
| Round Trips        | ✓          |            |             |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Multiple Bundle    |            |            | ✓           |            |            |
| Formats            |            |            |             |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Clipboard          | ✓          |            | ✓           | ✓          |            |
| Integration        |            |            |             |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Remote URL Support | ✓          | ✓          | ✓           |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Security Checks    | ✓          |            | ✓           |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Token Counting     |            | ✓          | ✓           | ✓          |            |
+--------------------+------------+------------+-------------+------------+------------+
| Token Optimization |            | ✓          | ✓           | ✓          | ✓          |
+--------------------+------------+------------+-------------+------------+------------+
| Config Files       | ✓          |            | ✓           | ✓          | ✓          |
+--------------------+------------+------------+-------------+------------+------------+
| .gitignore Support | ✓          | ✓          | ✓           | ✓          |            |
+--------------------+------------+------------+-------------+------------+------------+
| IDE Integration    |            |            | ✓           |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| API Available?     | ✓ [1]_     | ✓          |             |            |            |
+--------------------+------------+------------+-------------+------------+------------+
| Web Interface      |            | ✓          | ✓           |            |            |
+--------------------+------------+------------+-------------+------------+------------+

.. [1] API is not yet stable.


Extensions
-------------------------------------------------------------------------------

+----------------------------+------------+
| Extension                  | Type       |
+============================+============+
| Gitingest                  | Chrome     |
+----------------------------+------------+
| Gitingest                  | Firefox    |
+----------------------------+------------+
| Gitingest                  | Edge       |
+----------------------------+------------+
| Claude File Upload Helper  | Chrome     |
+----------------------------+------------+
| Repomix                    | VS Code    |
+----------------------------+------------+

Content Selection Approaches
===============================================================================

The tools follow two main philosophies for content selection:

Directory-Oriented
-------------------------------------------------------------------------------
**Tools**: Mimeogram, dump_dir, ai-digest

**Approach**:
  - Start with nothing
  - Add specific directories/files

**Implications**:
  - Better for targeted analysis or specific features
  - More precise control over context window usage
  - Easier to iteratively expand scope as needed
  - Better for ad-hoc exploration of large codebases
  - More manual control but less configuration needed
  - Well-suited for development work where relevant files are known

Repository-Oriented
-------------------------------------------------------------------------------
**Tools**: Gitingest, Repomix

**Approach**:
  - Start with entire repository
  - Filter out unnecessary directories/files

**Implications**:
  - Better for understanding full project context
  - Useful for initial project exploration
  - Requires careful configuration to avoid token limits
