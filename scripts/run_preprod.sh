#!/usr/bin/env bash
set -euo pipefail

# Detect docker compose command
if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
else
    DC="docker-compose"
fi

# Get command from first argument, default to 'up'
CMD="${1:-up}"

# Execute based on command
case "$CMD" in
    up)
        $DC -f docker-compose.preprod.yml up -d --build
        ;;
    down)
        $DC -f docker-compose.preprod.yml down
        ;;
    logs)
        $DC -f docker-compose.preprod.yml logs -f app
        ;;
    ps)
        $DC -f docker-compose.preprod.yml ps
        ;;
    restart)
        $DC -f docker-compose.preprod.yml restart
        ;;
    *)
        echo "Usage: $0 {up|down|logs|ps|restart}"
        echo "  up      - Start containers in detached mode with build"
        echo "  down    - Stop and remove containers"
        echo "  logs    - Follow application logs"
        echo "  ps      - List running containers"
        echo "  restart - Restart containers"
        exit 1
        ;;
esac
