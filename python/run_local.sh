#!/bin/bash

# Script to run the Hello World app with Dapr workflows
# Usage: ./run_local.sh [APP_ID]

APP_ID="${1:-hello-world-app}"
DAPR_VERSION="1.17.0-rc.2"

echo "Starting Hello World App with Dapr Workflows..."
echo "Using App ID: $APP_ID"

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "Dapr CLI not found. Installing Dapr CLI..."
    curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

    if command -v dapr &> /dev/null; then
        echo "Dapr CLI installed successfully"
    else
        echo "Error: Failed to install Dapr CLI. Please install manually:"
        echo "https://docs.dapr.io/getting-started/install-dapr-cli/"
        exit 1
    fi
else
    echo "Dapr CLI found: $(dapr version)"
fi

# Initialize Dapr if not already done
if [ ! -d "$HOME/.dapr" ]; then
    echo "Initializing Dapr..."
    dapr init --runtime-version "$DAPR_VERSION"
else
    echo "Dapr already initialized"
fi

# Find Python 3.10 or higher
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        if [ "$(printf '%s\n' "3.10" "$VERSION" | sort -V | head -n1)" = "3.10" ]; then
            PYTHON_CMD=$cmd
            PYTHON_VERSION=$VERSION
            echo "Found compatible Python: $PYTHON_CMD (version $PYTHON_VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.10 or higher is required but not found."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python $PYTHON_VERSION..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate
echo "Activated virtual environment"

# Clear Python bytecode caches
echo "Clearing Python bytecode caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Upgrade pip to support editable installs with pyproject.toml
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install the application in editable mode
echo "Installing application..."
pip install -e .
echo "Installation completed"

# Run with Dapr CLI
echo "Starting with Dapr CLI..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"
dapr run \
    --app-id "$APP_ID" \
    --app-port 8000 \
    --dapr-http-port 3500 \
    --dapr-grpc-port 50001 \
    --log-level debug \
    --resources-path "components" \
    -- "$SCRIPT_DIR/.venv/bin/python" -m hello_world_app.main

echo "Application stopped."
