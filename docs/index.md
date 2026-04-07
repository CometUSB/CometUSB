# CometUSB
##### _Python package for Linux distributions to create bootable USB._

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

## Purpose of CometUSB.
While this tool can be used with any terminal, mostly it is created for broken/corrupt system, so even if in the recovery environment user is unable to fix the system, a bootable device can be created right away from the same interface without even relying on the other system to make it, this makes the tool robust and reliable.

#### _Steps to work in broken system._
---
- Just boot into recovery mode from the GRUB menu while startup.
- Enable networking to have internet connection enabled.
- See the installation and usage guide to install and use respectively.
---


