# Internals: Working of CometUSB.

This document details the architecture, execution flow, and core logic behind the `cometusb` utility. It is intended for developers, contributors, and advanced users seeking a deep understanding of the project.

## 1. Core Workflow Pipeline

The entire process of creating the bootable drive is controlled by the **`Operating_System`** class and its public method, **`create()`**. The operation follows a strict, sequential 5-stage pipeline to ensure drive is properly bootable.

| Step | Function Executed | Purpose and Technical Details |
|:---|:---|:---|
| **1. Preparation** | `unmount_usb` | **Ensures Disk Access:** Uses `subprocess` to execute `umount` on all detected partitions of the target device (`/dev/device_name?`). This is critical to prevent "Device or resource busy" errors during the subsequent disk wipe. |
| **2. Formatting** | `format_disk` | **Partitioning and Filesystems:** Executes `sudo wipefs -a` to destroy the old partition table, then uses **`parted`** to create the new **GPT** or **MBR** table. Finally, `mkfs.fat` and `mkfs.ntfs` format the new partitions. |
| **3. Downloading** | `downloader` | **Reliable Fetching:** Uses the **`requests`** library with **`tqdm`** to download all required files (split images, archives, checksums) from the GitHub Releases server, providing a visual progress bar. |
| **4. Extraction** | `extractor` | **File Placement:** Extracts compressed archives (e.g., `boot.zip`) to the newly mounted partitions. Uses `tqdm` for extraction progress tracking. |
| **5. Bootloader** | `bootloader` | **Making it Bootable:** Installs the **GRUB** bootloader. The installation target is conditionally set to `x86_64-efi` for UEFI/GPT systems or `i386-pc` for Legacy/MBR systems. |


## 2. Low-Level Partitioning Logic

The tool's fundamental disk management is based on the user's choice of BIOS type, dictating the underlying partition table and filesystem layout.

| BIOS Type | Disk Standard |Partition Scheme |Partitions Label / Size / Filesystem | Rationale |
|:---|:---|:---|:---|:---|
| **UEFI** | **GPT** (GUID Partition Table) | Dual-Partition | 1. **COMET_BOOT**: 500 MiB, FAT32 (ESP). <br> 2. **COMET_FILES**: Remaining space, NTFS. | **Required for UEFI:** FAT32 ESP is mandatory for EFI firmware. **NTFS** is used for the data partition to overcome single-file size restriction. |
| **Legacy** | **MBR** (Master Boot Record) | Single-Partition | 1. **COMET**: Entire disk, NTFS. | **Simplicity:** A single NTFS partition is sufficient for **Legacy** booting and simplifies file management for the user. |

## 3. File Handling

The reliability of CometUSB heavily depends on its robust file handling.

#### Splitting OS image.
The large OS image like `filesystem.squashfs` file is downloaded in split parts (`filesystem.squashfs.aa`, `filesystem.squashfs.ab`, etc.). These parts are reconstructed using the Linux `cat` utility. The splitting is done to comply with the GitHub file size restriction for release pages i.e, Cannot store a file of size more than 2 GB.

#### Compressing of Contents.
There are plently(2000+) of smaller files essential for installation. So for reliable downloading, these files are archived into _**.zip**_ and uploaded.

#### Sequence of Downloading and Extraction.
---
- First Boot.zip which contains boot files required to boot is downloaded and extracted in the boot partition. Boot.zip is removed after extraction.
- Then directories.zip which contains all the smaller files is downloaded and extracted it also make the directories structure. directories.zip is also removed after the extraction.
- Spilitted OS images is then downloaded and merged via cat utility of linux and moved to the original required folder. This folder will be present beforehand after the extraction of directories.zip in earlier step above.
- All of these file read and write are done in the removable media itself, avoiding any overloading to the storage of the host system.
---

## 4. Source Code Mapping

| Component | Responsibility Area | Key Source Element |
|:---|:---|:---|
| **Application Flow** | Program entry point, argument parsing, OS object instantiation. | `cometusb.py` (`main` function). |
| **State Management** | Encapsulates all job data (OS, disk, partitions, files). | `cometusb.py` (`Operating_System` class). |
| **Disk Utilities** | Listing, Partitioning, formatting, unmounting, and mounting disk devices. | `cometusb.py` (`get_disk_details`, `format_disk`, `unmount_usb`, `mount_usb` functions). |
| **File Transfer** | Handling HTTP streams, progress tracking, and file extraction. | `cometusb.py` (`downloader`, `extractor` functions). |
| **Bootloader** | Applying **grub-install** on the disk as per given **BIOS** Type (**UEFI/Legacy**). | `bootloader` method in the Operating_System class applies the bootloader after checking the **BIOS** Type.|
