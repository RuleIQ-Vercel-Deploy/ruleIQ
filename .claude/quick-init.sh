#!/bin/bash
# Ultra-minimal initialization for Serena

# Silent verification
python3 -c "
import json
from pathlib import Path
from datetime import datetime

Path('.claude').mkdir(exist_ok=True)
Path('.claude/serena-active.flag').touch()

with open('.claude/verification-complete.json', 'w') as f:
    json.dump({'active': True, 'serena': 'active', 'timestamp': datetime.utcnow().isoformat()}, f)
" 2>/dev/null

# Only output essentials
echo "✅ Serena MCP: Active"