# Valon Tuner Jetson Service
This repo contains a systemd-managed telemetry service and CLI for the Valon 5015 RF Synthesizer designed 
for NVIDIA Jetson platforms. This service continously polls the valon to expose real-time telemetry via Unix domain socket.

There are two unix domain sockets opened by this service:
- Telemetry socket expecting another systemd service. Provides real-time frequency and power telemetry data for external clients or monitoring services (currently as a JSON string: ["TUNER", "freq", "power"]. A timestamp is also available (epoch)) 
- CLI command socket: Expects control commands from the [CLI](#4-run-the-cli)

## Installation for Service on Jetson

### Requirements:
- Python 3.8+
- Jetpack 6.2 Linux distro
- Valon 5015/5019 connected to linux machine
- pip3

### Setup: Create a persistent symlink for the Valon device
Create a udev file:
```bash
sudo nano /etc/udev/rules.d/99-valon.rules
```
Add the following:
```bash
SUBSYSTEM=="tty", ATTRS{idProduct}=="6001", ATTRS{idVendor}=="0403", SYMLINK+="valon5015"
```
Reload and apply udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## ONLINE Install

### 1. Clone this repo
```bash
git clone https://github.com/alisayurev/valon-jetson-service.git
cd Valon_Tuner
```

### 2. Run the Installer
```bash
chmod +x install.sh
./install.sh
```
This will install the package (`pip install`), generate the
valon_telem.service systemd unit, enable and start the service. NOTE: You need internet on your 
machine to be able to do this, as it runs `pip install --upgrade pip setuptools wheel`.
If you do not have internet: [see Offline Install](#offline-install).

## OFFLINE Install 

### 1. Clone this repo
On an online companion machine, clone the repo:
```bash
git clone https://github.com/alisayurev/valon-jetson-service.git
cd Valon_Tuner
```

### 2. Run the Installer
On your online machine:
```bash
pip install build
python3 -m build 
mkdir wheels 
cp dist/*.whl wheels/
pip download --dest wheels setuptools wheel
```
Copy the cloned repo (with /wheels within it) onto the offline machine:
```bash
./install --offline
```

### 3. Monitor service
```bash
sudo systemctl status valon_telem
```
See live logs:
```bash
journalctl -u valon_telem -f
```

### 4. Run the CLI
The CLI connects to the Unix socket opened in this service in order to set
parameters on the Valon. To run the CLI run the following in any directory:
```bash
valon-cli -f <FREQ_MHZ> -p <dB>
```
Frequency is a required argument, power is optional. The default power will be 0,
no amplification/attenuation. Test this on your own setup to edit the output accordingly. 
The range for -p is -50 to 20. In order to get more attenuation, another command needs to be added in valon_control. 
See [Valon 5015/5019 documentation](https://www.valonrf.com/5015-customer-downloads.html) for more details.

### To remove: 

```bash
rm -rf Valon_Tuner #remove the folder
pip uninstall valon_telem #uninstall package
sudo systemctl stop valon_telem #stop the service
sudo systemctl disable valon_telem
sudo rm /etc/systemd/system/valon_telem.service
sudo systemctl daemon-reload
```