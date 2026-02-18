/**
 * CORRECT Opencode plugin to run linters after file edits.
 * Port of Claude Code hook: template/.auxiliary/configuration/coders/claude/scripts/post-edit-linter
 */
export const PostEditLinterCorrect = async ({ project, client, $, directory, worktree }) => {
  /**
   * Checks if a command is available in PATH.
   */
  async function isCommandAvailable(command) {
    try {
      const result = await $`which ${command}`.nothrow().quiet();
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }

  /**
   * Checks if a specific Hatch environment exists.
   */
  async function isHatchEnvAvailable(envName) {
    try {
      const result = await $`hatch env show`.nothrow().quiet();
      if (result.exitCode !== 0) return false;
      return result.stdout.toString().includes(envName);
    } catch {
      return false;
    }
  }

  /**
   * Truncates output to maximum number of lines with truncation notice.
   */
  function truncateOutput(output, linesMax = 50) {
    const lines = output.split('\n');
    if (lines.length <= linesMax) return output;
    const linesToDisplay = lines.slice(0, linesMax);
    const truncationsCount = lines.length - linesMax;
    linesToDisplay.push(
      `\n[OUTPUT TRUNCATED: ${truncationsCount} additional lines omitted. ` +
      `Fix the issues above to see remaining diagnostics.]`
    );
    return linesToDisplay.join('\n');
  }

  /**
   * Runs a command with timeout using Promise.race.
   */
  async function runCommandWithTimeout(command, timeoutMs) {
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`Command timed out after ${timeoutMs}ms`)), timeoutMs);
    });

    try {
      const commandPromise = (async () => {
        try {
          // Use $ as tagged template function with shell execution
          // Pass the entire command as a shell command
          const result = await $`sh -c "${command}"`.nothrow().quiet();
          return {
            exitCode: result.exitCode,
            stdout: result.stdout?.toString() || '',
            stderr: result.stderr?.toString() || ''
          };
        } catch (error) {
          return {
            exitCode: error.exitCode || 1,
            stdout: error.stdout?.toString() || '',
            stderr: error.stderr?.toString() || error.message || ''
          };
        }
      })();

      return await Promise.race([commandPromise, timeoutPromise]);
    } catch (error) {
      return {
        exitCode: 1,
        stdout: '',
        stderr: error.message || 'Command execution failed'
      };
    }
  }

  return {
    "tool.execute.after": async (input, output) => {
      // Only run for edit tool
      if (input.tool !== "edit") return;

      // Get file path from output (not input!)
      const filePath = output?.metadata?.filediff?.file;
      if (!filePath) {
        // No file path in output, can't run linters
        return;
      }

      // Check if hatch command is available
      if (!(await isCommandAvailable('hatch'))) {
        return; // Early exit if hatch not available
      }

      // Check if develop Hatch environment exists
      if (!(await isHatchEnvAvailable('develop'))) {
        return; // Early exit if develop environment not available
      }

      try {
        // Run linters with 60 second timeout (matches Python script)
        const result = await runCommandWithTimeout(
          'hatch --env develop run linters',
          60000
        );

        if (result.exitCode !== 0) {
          // Combine stdout and stderr since linting output may go to stdout
          const resultText = `${result.stdout}\n\n${result.stderr}`.trim();
          const truncatedOutput = truncateOutput(resultText);
          
          // Throw error to show linter failures
          throw new Error(`Linters failed for ${filePath}:\n${truncatedOutput}`);
        }
      } catch (error) {
        // Re-throw the error with proper message
        if (error.message.includes('Command timed out')) {
          throw new Error(`Linter execution timed out for ${filePath}: ${error.message}`);
        }
        throw error;
      }
    }
  };
};