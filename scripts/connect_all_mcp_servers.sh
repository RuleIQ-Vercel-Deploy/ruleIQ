#!/bin/bash

# Script to connect all MCP servers defined in .mcp.json
# Usage: ./connect_all_mcp_servers.sh

echo "🚀 Connecting all MCP servers for ruleIQ project..."
echo "================================================"

# Desktop Commander
echo "📁 Starting Desktop Commander MCP..."
node /home/omar/DesktopCommanderMCP/dist/index.js &
DESKTOP_PID=$!
echo "   ✓ Desktop Commander started (PID: $DESKTOP_PID)"

# Serena - Project-specific code intelligence
echo "🧠 Starting Serena MCP for ruleIQ..."
/home/omar/.local/bin/uv run --directory /home/omar/serena serena start-mcp-server --project /home/omar/Documents/ruleIQ &
SERENA_PID=$!
echo "   ✓ Serena started (PID: $SERENA_PID)"

# Superdesign
echo "🎨 Starting Superdesign MCP..."
node -m superdesign_server &
SUPERDESIGN_PID=$!
echo "   ✓ Superdesign started (PID: $SUPERDESIGN_PID)"

# Fetch (via Smithery)
echo "🌐 Starting Fetch MCP..."
npx -y @smithery/cli@latest run @smithery-ai/fetch --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
FETCH_PID=$!
echo "   ✓ Fetch started (PID: $FETCH_PID)"

# Neon Database
echo "🗄️ Starting Neon Database MCP..."
npx -y @smithery/cli@latest run neon --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
NEON_PID=$!
echo "   ✓ Neon Database started (PID: $NEON_PID)"

# Shadcn Vue
echo "🖼️ Starting Shadcn Vue MCP..."
npx -y @smithery/cli@latest run @HelloGGX/shadcn-vue-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
SHADCN_PID=$!
echo "   ✓ Shadcn Vue started (PID: $SHADCN_PID)"

# Browser Tools
echo "🔧 Starting Browser Tools MCP..."
npx -y @smithery/cli@latest run @diulela/browser-tools-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
BROWSER_PID=$!
echo "   ✓ Browser Tools started (PID: $BROWSER_PID)"

# Mem0 Memory
echo "💭 Starting Mem0 Memory MCP..."
npx -y @smithery/cli@latest run @mem0ai/mem0-memory-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
MEM0_PID=$!
echo "   ✓ Mem0 Memory started (PID: $MEM0_PID)"

# Context7
echo "📚 Starting Context7 MCP..."
npx -y @smithery/cli@latest run @upstash/context7-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
CONTEXT7_PID=$!
echo "   ✓ Context7 started (PID: $CONTEXT7_PID)"

# PostgreSQL Database Management
echo "🐘 Starting PostgreSQL MCP..."
npx -y @smithery/cli@latest run @HenkDz/postgresql-mcp-server --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
POSTGRES_PID=$!
echo "   ✓ PostgreSQL MCP started (PID: $POSTGRES_PID)"

# Tavily
echo "🔍 Starting Tavily MCP..."
npx -y @smithery/cli@latest run @tavily-ai/tavily-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
TAVILY_PID=$!
echo "   ✓ Tavily started (PID: $TAVILY_PID)"

# Redis
echo "⚡ Starting Redis MCP..."
npx -y @smithery/cli@latest run @redis/mcp-redis --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
REDIS_PID=$!
echo "   ✓ Redis started (PID: $REDIS_PID)"

# Automated UI Debugger
echo "🐛 Starting UI Debugger MCP..."
npx -y @smithery/cli@latest run @samihalawa/visual-ui-debug-agent-mcp --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
UIDEBUG_PID=$!
echo "   ✓ UI Debugger started (PID: $UIDEBUG_PID)"

# GitHub
echo "🐙 Starting GitHub MCP..."
npx -y @smithery/cli@latest run @smithery-ai/github --key 95e83c85-9a18-4524-9549-6a2c0f194f69 --profile hungry-lemming-s64fT3 &
GITHUB_PID=$!
echo "   ✓ GitHub started (PID: $GITHUB_PID)"

# Archon - CRITICAL for task management
echo "🏛️ Starting Archon MCP (Task Management)..."
npx mcp-remote http://localhost:8051/mcp &
ARCHON_PID=$!
echo "   ✓ Archon started (PID: $ARCHON_PID)"

# TestSprite
echo "🧪 Starting TestSprite MCP..."
API_KEY="sk-user-b-dOi1HbRc33E1UXQrAsQac8Lw1jPX-T6HFKcweaEaC7avLKnobKlFyScXbEMaZHzGP_BXKmYmwwtnj-8qVO7jrTAw0oWcnWqXqecgMnLVzOgJgHOfckcXNn4sB2ySyjZwE" npx @testsprite/testsprite-mcp@latest &
TESTSPRITE_PID=$!
echo "   ✓ TestSprite started (PID: $TESTSPRITE_PID)"

echo ""
echo "================================================"
echo "✅ All MCP servers started successfully!"
echo ""
echo "Server PIDs:"
echo "  Desktop Commander: $DESKTOP_PID"
echo "  Serena: $SERENA_PID"
echo "  Superdesign: $SUPERDESIGN_PID"
echo "  Fetch: $FETCH_PID"
echo "  Neon Database: $NEON_PID"
echo "  Shadcn Vue: $SHADCN_PID"
echo "  Browser Tools: $BROWSER_PID"
echo "  Mem0 Memory: $MEM0_PID"
echo "  Context7: $CONTEXT7_PID"
echo "  PostgreSQL: $POSTGRES_PID"
echo "  Tavily: $TAVILY_PID"
echo "  Redis: $REDIS_PID"
echo "  UI Debugger: $UIDEBUG_PID"
echo "  GitHub: $GITHUB_PID"
echo "  Archon: $ARCHON_PID"
echo "  TestSprite: $TESTSPRITE_PID"
echo ""
echo "To stop all servers, run: ./stop_all_mcp_servers.sh"
echo "================================================"

# Save PIDs to a file for later cleanup
cat > /tmp/mcp_server_pids.txt << EOF
DESKTOP_PID=$DESKTOP_PID
SERENA_PID=$SERENA_PID
SUPERDESIGN_PID=$SUPERDESIGN_PID
FETCH_PID=$FETCH_PID
NEON_PID=$NEON_PID
SHADCN_PID=$SHADCN_PID
BROWSER_PID=$BROWSER_PID
MEM0_PID=$MEM0_PID
CONTEXT7_PID=$CONTEXT7_PID
POSTGRES_PID=$POSTGRES_PID
TAVILY_PID=$TAVILY_PID
REDIS_PID=$REDIS_PID
UIDEBUG_PID=$UIDEBUG_PID
GITHUB_PID=$GITHUB_PID
ARCHON_PID=$ARCHON_PID
TESTSPRITE_PID=$TESTSPRITE_PID
EOF

echo ""
echo "💡 PIDs saved to /tmp/mcp_server_pids.txt"
echo ""
echo "Now you can use Claude MCP CLI with all servers available!"
echo "Example: mcp list"