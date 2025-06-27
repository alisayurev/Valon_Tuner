# Valon Tuner Jetson Service
This repo contains a systemd managed telemetry service and CLI interface for the Valon 5015 RF Synthesizer.
This service continously polls the valon + exposes telemetry via Unix socket.

## Installation
### 1. Requirements:
- Python 3.8+
- systemd linux distribution
- Valon 5015/5019 connected to linux machine
- pip3

### 2. Clone this repo
```bash
git clone --single-branch --branch jetson-service https://github.com/alisayurev/Valon_Tuner.git
cd Valon_Tuner
```

### 3. Run the installer
As of now, the service requires the valon to be plugged in on boot. 
```bash
chmod +x install.sh
./install.sh
```
This will install the package in editable mode (`pip install -e`), generate the
valon_telem.service systemd unit, enable and start the service. 

### 4. Monitor service
```bash
sudo systemctl status valon_telem
```
See live logs:
```bash
journalctl -u valon_telem -f
```

### 5. Run the CLI
The CLI connects to the Unix socket opened in this service in order to set
parameters on the Valon. 


