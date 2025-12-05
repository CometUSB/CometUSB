# CometUSB
##### _Python package for Linux distributions to create bootable USB._

## Description
This is a python package exclusively for linux distributions. It has list of linux distributions you can choose to create the bootable media. In the corresponding release section you will find the installation files of several linux distributions. 
<br>
_Note: Minimum 8GB of Disk required to proceed_

## Installation
```bash
pip install cometusb
or
python -m pip install cometusb
or
python3 -m pip install cometusb
or 
apt install python3-cometusb 
```
_If none of the above commands work, find out how to install python package in your system._

## Usage
`sudo cometusb -o <OS_Name> -b <BIOS_Type>`
<br>
or
<br>
`sudo cometusb --operating-system <OS_Name> --bios-type <BIOS_TYPE>`

_e.g, `sudo cometusb -o linuxmint -b uefi`_

_Type `cometusb -h` to see the usage_

---
## Features

- Create UEFI with GPT and Legacy BIOS with MBR bootable USBs.
- Dual-partition layout: In case of UEFI system two partitions first small FAT32 for boot then NTFS in rest of the space for other files are created.
- Single-partition layout: In case of legacy systems only one NTFS partition is created in the entire disk for both boot and installation files.
- Automatically install GRUB for UEFI or legacy systems.
- Works with many Linux distros (Ubuntu family, Debian, Fedora, Arch, etc.)
- Handles `filesystem.squashfs` splitting/merging workflows
- Only shows removable disk to format which prevents wiping your main HDD/SSD. This avoids significant data loss.

---


