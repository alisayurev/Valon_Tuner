# Valon Tuner Jetson Service
This repo contains a systemd managed telemetry service and CLI interface for the Valon 5015 RF Synthesizer.
This service continously polls the valon + exposes telemetry via Unix socket.

## Installation for Service on Jetson

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

### 3. Run the Installer (ONLINE)
As of now, the service requires the valon to be plugged in on boot. 
```bash
chmod +x install.sh
./install.sh
```
This will install the package (`pip install`), generate the
valon_telem.service systemd unit, enable and start the service. NOTE: You need internet on your 
machine to be able to do this, as it runs `pip install --upgrade pip setuptools wheel`.
If you do not have internet: [see Offline Install](#35-run-the-installer-offline). If your machine already has Pyserial in a
python environment, you can edit the pyproject.toml to remove this dependency and continue with regular install.

### 3.5 Run the Installer (OFFLINE)
In order to install this offline, an online companion machine must [clone this repo](#2-clone-this-repo), and 
`cd` into Valon_Tuner. Then download the packages:
```bash
pip download --dest wheels
```
Copy `/wheels' directory onto the offline machine, and run:
```bash
./install --offline
```

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
parameters on the Valon. To run the CLI run the following in any directory:
```bash
valon-cli -f <FREQ_MHZ> -p <dB>
```
Frequency is a required argument, power is optional. The default power will be 0,
no amplification/attenuation. Test this on your own setup to edit the output accordingly. 
The range for -p is -50 to 20. In order to get more attenuation, another command needs to be added in valon_control. 
See [Valon 5015/5019 documentation](https://www.valonrf.com/5015-customer-downloads.html) for more details.

## Alternate Installation (development/CLI use only)
```bash
pip install git+https://github.com/alisayurev/Valon_Tuner.git@jetson-service
```
This will clone the repo and build the python package valon_telem. This doesnt start up the systemd service. 
