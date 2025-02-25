#!/bin/bash
INSTANCE_DIR="/var/lib/rinbot"

mkdir -p "$INSTANCE_DIR/logs/lavalink"
mkdir -p "$INSTANCE_DIR/cache"

chmod -R 777 "$INSTANCE_DIR"

echo "Lavalink instance directory structure initialized successfully."
echo "Structure:"
find "$INSTANCE_DIR" -type d | sort

exec "$@"