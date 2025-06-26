#!/bin/bash
set -e

SERVICE_NAME="valon-telem"
SERVICE_TEMPLATE="systemd/valon_telem.service.template"
USER=$(whoami)                        
WORKDIR="$(pwd)"   
echo "Installing Python package..."

# assumes you're running from your repo root where pyproject.toml lives
pip install --upgrade pip setuptools wheel
pip install -e "$WORKDIR"

echo "Copying systemd service file..."
sed "s|USER_PLACEHOLDER|$USER|g; s|WORKDIR_PLACEHOLDER|$WORKDIR|g" "$SERVICE_TEMPLATE" | sudo tee "$SERVICE_PATH" > /dev/null

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting $SERVICE_NAME service..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Check status with:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "And view logs with:"
echo "  journalctl -u $SERVICE_NAME -f"
