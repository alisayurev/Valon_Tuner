# Valon Tuner
Python CLI to control the Valon Tuner from the terminal.

## Dependencies
Ensure you have Python3 and pip3 installed. Then:
### 1. Install Pyserial
```bash
pip3 install pyserial
```
### 2. Create a udev rule for persistant naming
Create the rule file:
```bash
sudo nano /etc/udev/rules.d/99-valon.rules
```
Add the following line:
```bash
SUBSYSTEM=="tty, ATTRS{idProduct}=="6001", ATTRS{idVendor}=="0403", SYMBLINK+="valon5015"
```
Reload and apply udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

If this doesn't work, check if the simlink was created
```bash
ls -l /dev/valon5015
```
You may have to find the attributes manually, and copy them into the rule file:
```bash
udevadm info --name=/dev/ttyUSB0 --attribute-walk`
```

## Usage
Make the script executable:
```bash
chmod +x tuner_valon.py
```
Now you can run it with:
```bash
./tuner_valon.py -f <FREQ> -p <PWR>`
```
Frequency is a required parameter, while power is optional. The default gain/attentuation 
is 0.

## Notes:
- To persist synthesizer configuration across reboots, send the "SAV" command. This will store the current state in non-volatile memory.
- You can expand this tool to support sweep mode, reference source control, locking, and output enable (OEN) as needed.
- See the [Valon 5015/5019 documentation](https://www.valonrf.com/5015-customer-downloads.html) for valid ranges and additional commands.
- This script requires Linux for the persistent device naming via udev. The core script could work on Windows and MacOS but will need editing for opening the serial port.