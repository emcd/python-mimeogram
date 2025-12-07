# Claude Code (Web) Session Setup

**Instructions for Claude instances**: Execute the following setup steps at the beginning of each Claude Code (Web) session to ensure all required tools are available.

## Required Setup Steps

### 1. Install System Packages

Install GitHub CLI from the latest release (ensures latest version instead of older Ubuntu package).

First, get the latest version number:

```bash
wget https://github.com/cli/cli/releases/latest -O - 2>&1 | grep -oP 'href="/cli/cli/releases/tag/v\K[0-9.]+' | head -1
```

Then download and install, substituting the version number from above:

```bash
wget -O /tmp/gh_VERSION_linux_amd64.deb https://github.com/cli/cli/releases/download/vVERSION/gh_VERSION_linux_amd64.deb
```

```bash
dpkg -i /tmp/gh_VERSION_linux_amd64.deb
```

### 2. Install Core Python Tools

```bash
uv tool install hatch
uv tool install copier
uv tool install emcd-agents
```

### 3. Populate Project Agents

```bash
agentsmgr populate project github:emcd/agents-common@master#defaults
```

### 4. Configure Environment

Set up Go paths for persistent access. Append to `~/.local/bin/env`:

```bash
cat >> ~/.local/bin/env << 'EOF'

# Add Go bin to PATH
export GOPATH="${HOME}/.local/share/go"
case ":${PATH}:" in
    *:"${GOPATH}/bin":*)
        ;;
    *)
        export PATH="${GOPATH}/bin:${PATH}"
        ;;
esac
EOF
```

Source the updated environment:

```bash
source ~/.local/bin/env
```

### 5. Install Language Servers

Install `mcp-language-server` (proxies language servers for MCP):

```bash
go install github.com/isaacphi/mcp-language-server@latest
```

Install Pyright (Python language server):

```bash
npm install -g pyright
```

Install Ruff (Python linter/formatter):

```bash
uv tool install ruff
```

### 6. Setup Bash Tool Bypass Wrapper

Copy the bash-tool-bypass script to PATH for accessing restricted commands:

```bash
cp .auxiliary/configuration/coders/claude/miscellany/bash-tool-bypass ~/.local/bin/
chmod +x ~/.local/bin/bash-tool-bypass
```

## Notes

- The `.mcp.json` configuration expects these tools to be in PATH
- The `bash-tool-bypass` wrapper enables execution of commands restricted by Claude Code Bash tool permissions
