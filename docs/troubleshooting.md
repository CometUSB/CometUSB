# Troubleshooting

Here are solutions for common issues encountered when using CometUSB:

### 1. Permission Denied

**Error:** `PermissionError: [Errno 13] Permission denied` or general failures when accessing `/dev/sdX`.

**Solution:** CometUSB must manage disk devices, which requires root access. Always run the tool using `sudo`.

e.g, `sudo cometusb -o linuxmint -b uefi`

### 2. Active Internet Connection

This tool downloads the installation files from the github release. Make
sure you have a working and stable connection.

### 3. Storage Required

This tools downloads the files in the removable disk and do all the operations like extracting, merging the OS image files in the disk itself, so that it does not rely on the host system to store the files. Therefore, before wiping the disk out it a confirmation option will be prompted, there you can see the size of the disk required, make sure you have atleast that much size of disk.

### 4. Firmware Detection
