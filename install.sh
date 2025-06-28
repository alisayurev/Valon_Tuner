#!/bin/bash
set -e

SERVICE_NAME="valon_telem"
SERVICE_TEMPLATE="systemd/valon_telem.service.template"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
USER=$(whoami)                        
WORKDIR="$(pwd)"   
echo "Installing Python package..."

OFFLINE=0 #assumes online

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Use sudo:"
    echo "  sudo $0"
    exit 1
fi

if [[ "$1" == "--offline" ]]; then
    OFFLINE=1
    echo "offline install"
else 
    echo "online install"
fi

if [[ $OFFLINE -eq 0 ]]; then
    # assumes you're running from root where pyproject.toml lives
    # this part assumes internet access
    pip install --upgrade pip setuptools wheel
    pip install "$WORKDIR"
else
    pip install --no-index --find-links=wheels "$WORKDIR"

fi

echo "Copying systemd service file..."
if ! sed "s|USER_PLACEHOLDER|$USER|g; s|WORKDIR_PLACEHOLDER|$WORKDIR|g" "$SERVICE_TEMPLATE" | tee "$SERVICE_PATH" > /dev/null; then
    echo "Error: Failed to write service file to $SERVICE_PATH"
    exit 1
fi

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting $SERVICE_NAME service..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Check status with:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "And view logs with:"
echo "  journalctl -u $SERVICE_NAME -f"
