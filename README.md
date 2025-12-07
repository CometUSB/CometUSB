# CometUSB
##### _Python package for Linux distributions to create bootable USB._
_**See full documentation at: https://CometUSB.github.io/CometUSB/**_
## Description
This is a python package exclusively for linux distributions. It has list of linux distributions you can choose to create the bootable media. In the corresponding release section you will find the installation files of several linux distributions. 

## Features
---
- Create UEFI with GPT and Legacy BIOS with MBR bootable USBs.
- Dual-partition layout: In case of UEFI system two partitions first small FAT32 for boot then NTFS in rest of the space for other files are created.
- Single-partition layout: In case of legacy systems only one NTFS partition is created in the entire disk for both boot and installation files.
- Automatically install GRUB for UEFI or legacy systems.
- Only shows removable disk to format which prevents wiping your main HDD/SSD. This avoids significant data loss.

---

# Installation

CometUSB is a Python package available on PyPI. It requires Python 3.8 or higher.

### Prerequisites

Before installation, ensure you have:

* **Linux Distribution:** CometUSB is exclusively for Linux.
* **Python 3.8+:** Installed on your system.
* **Administrative Rights (`sudo`):** The tool requires `sudo` privileges to manage disks and partitions.

### Install via pip

The most straightforward way to install CometUSB is using `pip`:

```bash
pip install cometusb
or
# Using python -m pip (recommended for virtual environments)
python -m pip install cometusb
or
python3 -m pip install cometusb
```
_If none of the above commands work, find out how to install python package in your system._

# Usage Guide

CometUSB is run directly from the command line, requiring administrative privileges (`sudo`) because it must access and format your physical disk devices.

### Basic Command Structure

You must always specify the Operating System name (`-o`) and the target system's BIOS type (`-b`).


`sudo cometusb -o <OS_NAME> -b <BIOS_TYPE>`

or

`sudo cometusb --operating-system <OS_Name> --bios-type <BIOS_TYPE>`

_e.g, `sudo cometusb -o linuxmint -b uefi`_

_Type `cometusb -h` or `cometusb --help` to see the usage_

_Type `cometusb --list-os` or `cometusb -l` to see the list of available Operating System_

# CLI Reference
![alt text](/docs/img/cli.png)
### Required Arguments

| Option | Long Option | Description | Example |
| :--- | :--- | :--- | :--- |
| `-o` | `--operating-system` | **Name of the Operating System** to download and install.| `-o linuxmint` |
| `-b` | `--bios-type` | **BIOS type** (boot mode) for the target system. Specifies the partitioning scheme (GPT/MBR) and GRUB installation method. | `-b uefi` |

### Optional Arguments

| Option | Long Option | Description |
| :--- | :--- | :--- |
| `-l` | `--list-os` | Shows a list of the currently available and supported Operating Systems. |
| `-h` | `--help` | Show the help message and exit. |
