#!/usr/bin/env node

// MCP Control Center - Claude Code Integration
// This script provides the /mcp-control command interface

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const **filename = fileURLToPath(import.meta.url);
const **dirname = path.dirname(\_\_filename);

const args = process.argv.slice(2);
const command = args[0];
const target = args[1];
const options = args.slice(2);

const API_URL = process.env.MCP_API_URL || 'http://localhost:3001';

async function executeCommand(cmd, params = {}) {
try {
const response = await fetch(`${API_URL}/api/mcp/execute`, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ command: cmd, ...params })
});

    const result = await response.json();

    if (result.success) {
      console.log(result.stdout || 'Command executed successfully');
    } else {
      console.error('Error:', result.error);
      process.exit(1);
    }

} catch (error) {
console.error('Failed to connect to MCP Control Center:', error.message);
console.log('Starting MCP Control Center server...');
startServer();
}
}

function startServer() {
const serverProcess = spawn('npm', ['start'], {
cwd: \_\_dirname,
detached: true,
stdio: 'ignore'
});

serverProcess.unref();
console.log('MCP Control Center server starting on http://localhost:3001');

setTimeout(() => {
openUI();
}, 3000);
}

function openUI() {
const url = 'http://localhost:5173';
const start = process.platform === 'darwin' ? 'open' :
process.platform === 'win32' ? 'start' : 'xdg-open';

spawn(start, [url], { detached: true }).unref();
console.log(`MCP Control Center UI opened at ${url}`);
}

async function main() {
if (!command || command === 'help') {
console.log(`
MCP Control Center - Command Line Interface

Usage: /mcp-control [command] [target] [options]

Commands:
status Show status of all MCP servers
start [server|all] Start specific server or all servers
stop [server|all] Stop specific server or all servers
restart [server] Restart specific server
health Run health check
projects List MCP-enabled projects
ui Open the web UI
help Show this help message

Servers:
serena Serena MCP Server
archon Archon Server
playwright Playwright MCP
docker Docker MCP Gateway

Examples:
/mcp-control status
/mcp-control start serena
/mcp-control stop all
/mcp-control ui
`);
return;
}

switch (command) {
case 'ui':
openUI();
break;

    case 'status':
      const statusResponse = await fetch(`${API_URL}/api/mcp/servers`);
      const servers = await statusResponse.json();
      console.log('MCP Server Status:');
      Object.entries(servers).forEach(([key, server]) => {
        const status = server.status === 'running' ? '✓ Running' : '✗ Stopped';
        console.log(`  ${status} - ${server.name}`);
        if (server.status === 'running') {
          console.log(`    PID: ${server.pid}, Memory: ${server.memory}MB`);
        }
      });
      break;

    case 'start':
    case 'stop':
    case 'restart':
      if (!target) {
        console.error(`Error: Please specify a server name or 'all'`);
        process.exit(1);
      }

      if (target === 'all') {
        const serversResponse = await fetch(`${API_URL}/api/mcp/servers`);
        const servers = await serversResponse.json();

        for (const serverName of Object.keys(servers)) {
          console.log(`${command}ing ${serverName}...`);
          await fetch(`${API_URL}/api/mcp/servers/${serverName}/${command}`, {
            method: 'POST'
          });
        }
      } else {
        console.log(`${command}ing ${target}...`);
        const response = await fetch(`${API_URL}/api/mcp/servers/${target}/${command}`, {
          method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
          console.log(`Successfully ${command}ed ${target}`);
        } else {
          console.error(`Failed to ${command} ${target}:`, result.error);
        }
      }
      break;

    case 'health':
      const healthResponse = await fetch(`${API_URL}/api/mcp/health`);
      const health = await healthResponse.json();
      console.log('System Health Check:');
      console.log(`  Memory Usage: ${health.memoryUsage}MB`);
      console.log(`  Zombie Processes: ${health.zombieProcesses}`);
      console.log(`  Port Conflicts: ${health.portConflicts.length}`);
      console.log(`  Duplicate Processes: ${health.duplicateProcesses.length}`);
      break;

    case 'projects':
      const projectsResponse = await fetch(`${API_URL}/api/mcp/projects`);
      const projects = await projectsResponse.json();
      console.log('MCP-Enabled Projects:');
      projects.forEach(project => {
        console.log(`  - ${project.name}`);
        console.log(`    Path: ${project.path}`);
      });
      break;

    default:
      console.error(`Unknown command: ${command}`);
      console.log('Run "/mcp-control help" for usage information');
      process.exit(1);

}
}

main().catch(console.error);
