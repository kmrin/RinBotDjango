#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_FILE="$SCRIPT_DIR/../lavalink/config/rinbot.yml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

if ! python -c "import yaml" &> /dev/null; then
    echo "PyYAML is required. Installing..."
    pip install pyyaml
fi

echo "Loading database configuration from rinbot.yml..."

export DB_NAME=$(python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
print(config.get('database', {}).get('name', 'rinbot'))
")

export DB_USER=$(python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
print(config.get('database', {}).get('user', 'rinbot'))
")

export DB_PASSWORD=$(python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
print(config.get('database', {}).get('password', 'rinbotpassword'))
")

export DB_HOST=$(python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
print(config.get('database', {}).get('host', 'rinbot-postgres'))
")

export DB_PORT=$(python -c "
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
print(config.get('database', {}).get('port', '5432'))
")

export POSTGRES_DB=$DB_NAME
export POSTGRES_USER=$DB_USER
export POSTGRES_PASSWORD=$DB_PASSWORD
