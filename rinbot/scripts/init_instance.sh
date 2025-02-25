#!/bin/bash
echo "Loading configuration from rinbot.yml..."
INSTANCE_DIR=$(python -c "import sys; sys.path.insert(0, '/app'); from config import instance_config;")

echo "Using instance directory: $INSTANCE_DIR"

mkdir -p "$INSTANCE_DIR"

python -c "
import sys
sys.path.insert(0, '/app')
from config import instance_config
base_dir = instance_config.get('base_dir', '/var/lib/rinbot')
for subdir in instance_config.get('subdirs', []):
    print(f'{base_dir}/{subdir}')
" | xargs -I{} mkdir -p {}

chmod -R 777 "$INSTANCE_DIR"

echo "Instance directory structure initialized successfully."
echo "Structure:"
find "$INSTANCE_DIR" -type d | sort

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL is not ready yet - sleeping for 1 second"
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
python manage.py migrate

exec "$@"
