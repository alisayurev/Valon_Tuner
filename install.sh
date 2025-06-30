#!/bin/bash
set -e

SERVICE_NAME="valon_telem"
SERVICE_TEMPLATE="systemd/valon_telem.service.template"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
USER=$(whoami)                        
WORKDIR="$(pwd)"   
echo "Installing Python package..."
OFFLINE=0 #assumes online

if [[ "$1" == "--offline" ]]; then
    OFFLINE=1
    echo "offline install"
else 
    echo "online install"
fi

## TO DO: test online install on a MEP
if [[ $OFFLINE -eq 0 ]]; then
    # assumes you're running from root where pyproject.toml lives
    # this part assumes internet access
    pip install --upgrade pip setuptools wheel
    pip install "$WORKDIR"
else
    WHEEL_FILE=$(ls wheels/valon_telem-*.whl | head -n 1)
    echo "Installing: $WHEEL_FILE"
    pip install --no-index --find-links=wheels "$WHEEL_FILE"

fi

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
