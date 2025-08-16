# Cipher Aggregator Mode Setup Guide

## Overview
Cipher has been configured to run in **Aggregator Mode**, which allows it to combine multiple MCP servers into a single unified interface.

## What is Aggregator Mode?
In Aggregator Mode, Cipher acts as a hub that:
- Provides its own memory and search capabilities (`ask_cipher`, `cipher_search_memory`)
- Aggregates tools from other MCP servers (like filesystem operations)
- Presents all tools through a single MCP endpoint

## Configuration Files

### 1. Batch Files for Running Cipher
- **`test_cipher.bat`** - Updated with aggregator mode environment variables
- **`run_cipher_aggregator.bat`** - Dedicated script for running Cipher in aggregator mode

### 2. Cipher Configuration
- **`cipher-source/memAgent/cipher.yml`** - Contains:
  - LLM configuration (Gemini)
  - Embedding configuration
  - MCP servers to aggregate (currently filesystem server)

### 3. Client Configuration Example
- **`mcp-client-config-example.json`** - Template for configuring MCP clients like:
  - Claude Desktop
  - Cursor
  - Other MCP-compatible IDEs

## How to Run

### Quick Start
1. Run the aggregator:
   ```batch
   run_cipher_aggregator.bat
   ```

2. The server will start with:
   - MCP_SERVER_MODE=aggregator
   - Filesystem tools enabled
   - Memory capabilities active

### Adding More MCP Servers
Edit `cipher-source/memAgent/cipher.yml` and add servers under `mcpServers`:

```yaml
mcpServers:
  filesystem:
    # ... existing config ...
    
  # Add new server example:
  github:
    type: stdio
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-github'
    env:
      GITHUB_TOKEN: ${GITHUB_TOKEN}
```

## Environment Variables
Key environment variables set in aggregator mode:
- `MCP_SERVER_MODE=aggregator` - Enables aggregator mode
- `AGGREGATOR_CONFLICT_RESOLUTION=prefix` - Handles tool name conflicts
- `AGGREGATOR_TIMEOUT=120000` - 2-minute timeout for tool execution

## Available Tools
In aggregator mode, you get:
1. **Cipher Memory Tools**:
   - `ask_cipher` - Query Cipher's memory
   - `cipher_search_memory` - Search stored memories
   - `cipher_extract_and_operate_memory` - Store new memories

2. **Filesystem Tools** (from @modelcontextprotocol/server-filesystem):
   - File reading/writing
   - Directory listing
   - File operations

## Troubleshooting
If tools don't appear in your MCP client:
1. Ensure `MCP_SERVER_MODE=aggregator` is set
2. Check that `cipher.yml` is in the correct location
3. Restart your MCP client after configuration changes
4. Verify API keys are set correctly

## Integration with IDEs
For Claude Desktop or Cursor:
1. Copy `mcp-client-config-example.json` content
2. Update paths to match your system
3. Add your API keys
4. Paste into your IDE's MCP configuration