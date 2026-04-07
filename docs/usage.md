# Usage Guide

CometUSB is run directly from the command line, requiring administrative privileges (`sudo`) because it must access and format your physical disk devices.

### Basic Command Structure

You must always specify the Operating System name (`-o`) and the target system's BIOS type (`-b`).


`sudo cometusb -o <OS_NAME> -b <BIOS_TYPE>`

or

`sudo cometusb --operating-system <OS_Name> --bios-type <BIOS_TYPE>`

_e.g, `sudo cometusb -o linuxmint -b uefi`_

If using virtual environment (venv), use `sudo su` like below.
```bash
thesniper@thesniperpc:~$ sudo su
[sudo] password for thesniper:   
root@thesniperpc:/home/thesniper source .venv/bin/activate # Give your virtual environemnt path if different. 
(.venv) root@thesniperpc:/home/thesniper cometusb -o linuxmint -b uefi
```

_Type `cometusb -h` or `cometusb --help` to see the usage_

_Type `cometusb --list-os` or `cometusb -l` to see the list of available Operating System_