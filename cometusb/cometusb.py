import subprocess
import json
import sys
import argparse
import glob
from tabulate import tabulate
import requests
from tqdm import tqdm
import zipfile as zf
import os

def main():
# Make case insensitive cmdline arguements
    
    parser = argparse.ArgumentParser(
                    prog= "CometUSB.",
                    description="Create linux bootable USB."
                    )
    parser.add_argument("-l", "--list-os", help="Shows list of the available Operating Systems.")
    parser.add_argument("-o", "--operating-system", help="Name of the Operating System.")
    parser.add_argument("-b","--bios-type", help="BIOS type (e.g., UEFI or Legacy), check what your TARGET SYSTEM supports.")
    args = parser.parse_args()

    operating_system = Operating_System(args.operating_system.lower(), args.bios_type.lower())
    print(operating_system)
    operating_system.create()
    
class Operating_System():
    def __init__(self, name, bios_type):
        self.name = name
        self.bios_type = bios_type
        self.partition_style = bios_type
        self.target_disk = get_disk_details()
        self.disk_partitions = format_disk(self.target_disk, self.bios_type) # Dictionary of newly created partitions with labels
        self.files = self.name
        self._path_url = f"https://github.com/CometUSB/CometUSB/releases/download/{self.name}/"
        self._architecture= "64 Bit"
        

    def __str__(self):
        return f"\nOS = {self.name.upper()}\nArchitecture = {self._architecture}\nBIOS Type = {self.bios_type}\nTarget Device = {self.target_disk}\nPartition Style = {self.partition_style.upper()}\nFiles to be Downloaded = {[name for name in self.files.keys()]}\n"
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        OS = ["linuxmint"]
        if name not in OS:
            sys.exit("[!] Invalid or Unsupported Operating System.\nEnter 'cometusb.py --OS-list' without quotes to see the supported list of Operating systems")

        self._name = name
    
    @property
    def partition_style(self):
        return self._partition_style
    
    @partition_style.setter
    def partition_style(self, bios_type):
        if bios_type == "uefi":
            self._partition_style = "GPT"

        elif bios_type == "legacy":
            self._partition_style = "MBR"

        else:
            sys.exit("[!] Invalid BIOS type.")
        

    @property
    def files(self):
        return self._files
    
    @files.setter
    def files(self, name):
        
        if len(self.disk_partitions) == 2:
            boot_partition, file_partition = self.disk_partitions.keys()
        elif len(self.disk_partitions) == 1:
            file_partition = [partition for partition in self.disk_partitions.keys()][0] # files_partition and boot_partition are the labels of boot partition and files partitions
            boot_partition = file_partition
        OS_FILES = {
        "linuxmint": {
            "boot.zip": f"/mnt/{boot_partition}/",
            "directories.zip":f"/mnt/{file_partition}/",
            "filesystem.squashfs.aa": f"/mnt/{file_partition}/",
            "filesystem.squashfs.ab": f"/mnt/{file_partition}/"
        }
        }

        self._files = OS_FILES[name]

    @property
    def target_disk(self):
        return self._target_disk
    
    @target_disk.setter
    def target_disk(self, target_disk):
        self._target_disk = target_disk

    @property
    def disk_partitions(self):
        return self._disk_partitions
        
    @disk_partitions.setter
    def disk_partitions(self, partitions):
        self._disk_partitions = partitions
        
    def create(self):
        create_disk(self.files, self.target_disk, self.disk_partitions, self._path_url)

def create_disk(files, target_disk, disk_partitions, path_url):
    mount_usb(disk_partitions)

    # Disk configuration info. 
    print(f"\n[*] Disk {target_disk} configuration.")
    subprocess.run(["lsblk", target_disk, "-o", "NAME,SIZE,FSTYPE,FSVER,LABEL,MOUNTPOINTS"])

    for filename, download_dir in files.items():
        print() #To create gap between progress bars.
        print(f"Downloading {filename} into {download_dir}")
        downloader(path_url + filename, download_dir)
        print() #To create gap between progress bars.
        if filename.endswith(".zip"):
            # Extracting to create the directory tree structure
            extractor(download_dir + filename, download_dir)
            print() #To create gap between progress bars.
            os.remove(download_dir + filename) # Removing the zip file after extracting to free space in the USB.
        if filename.endswith(".aa"):
            image_name, download_dir = filename.rstrip(".aa"), download_dir
    print(f"[*] Making OS Image {image_name} ready for installation.\n[*] This may take a while depending upon your removable disk {target_disk}.")
    subprocess.run(f"sudo cat {download_dir}{image_name}.* > {download_dir}casper/{image_name}", shell=True, stdout=subprocess.DEVNULL)

    print("[*] Cleaning unnecessary file...")
    for splitted_image_file in glob.glob(f"{download_dir}{image_name}.*"):
        os.remove(splitted_image_file)
        
    print("Media created succesfully\nNOTE: Linux disk sometimes is not detected in BIOS, try disabling secure boot of your BIOS if facing any issues while booting.")




def get_disk_details():
    """
    Executes the 'lsblk' command to retrieve detailed information for physical
    block disks using JSON output for robust, programmatic parsing.
    
    The -J flag outputs clean JSON, which avoids parsing issues related to 
    variable column spacing and locales common with plain text output.
    """
    # Arguments explained:
    # -d: Display only the main disk disks (e.g., sda, sdb), not partitions.
    # -J: Output in JSON format (essential for easy, stable parsing).
    # -o: Specify the output columns: NAME, SIZE, VENDOR, and MODEL.
    LSBLK_CMD = ['lsblk', '-d','-J', '-o', 'NAME,SIZE,VENDOR,MODEL,RM']

   
    # Execute the command, capture output, and ensure success
    result = subprocess.run(
        LSBLK_CMD, 
        capture_output=True, 
        text=True,
        check=True
    )
    
    # Parse the JSON output into a Python dictionary
    data = json.loads(result.stdout)
    
    # Extract and filter the block disks
    

    disks = [
                [
                    disk.get('name', 'N/A'), 
                    disk.get('size', 'N/A'),
                    disk.get('vendor', 'N/A'),
                    disk.get('model', 'N/A')
                ]
                for disk in data.get('blockdevices', []) if disk.get('rm', 'N/A') == True
            ]
    
    if not disks:
        sys.exit("No USB/removable media found.")
    headers = [header.capitalize() for header in data.get("blockdevices")[0].keys()]
    headers[2] = "Interface" # Renaming Vendor column to Interface
    print(tabulate(disks, headers=headers, tablefmt="grid"))

    
    return f"/dev/{input("Enter disk: ")}"



def format_disk(disk, bios_type):
     # Confirming to Format the USB
    print(f"\n[*] This will ERASE all data on {disk}") 
    if input("Type 'yes' to continue: ").strip().lower() != "yes":
        sys.exit("Aborted by user.")

    partitions = glob.glob(disk + "?")
    unmount_usb(partitions)
    try:

        # Wipe partition table
        print(f"\n[*] Wiping disk {disk}")
        subprocess.run(["sudo", "wipefs", "-a", disk], check=True)

        print(f"\n[*] Creating partitions for {bios_type} systems...")
        if bios_type == "uefi":
            # Create new partition table and partition
            subprocess.run(["sudo", "parted", "-s", disk, "mklabel", "gpt"], check=True)
            subprocess.run(["sudo", "parted", "-s", disk, "mkpart", "primary", "1MiB", "1001MiB"], check=True)
            partition = glob.glob(disk + "?")
            boot_partition = partition[0]
            subprocess.run(["sudo", "parted", "-s", disk, "mkpart", "primary", "1001MiB", "100%"], check=True)
            partition = glob.glob(disk + "?")
            partition.remove(boot_partition)
            files_partition = partition[0]

            # Refreshing the partitions
            subprocess.run(["sudo", "partprobe", disk], check=True)
            subprocess.run(["sudo", "udevadm", "settle"], check=True)

            # Creating the filesystems
            print(f"\n[*] Creating filesystems ...")
            subprocess.run(["sudo", "mkfs.fat", "-F", "32", "-n", "COMET_BOOT", boot_partition], check=True)
            subprocess.run(["sudo", "parted", "-s", disk, "set", "1", "esp", "on"], check=True)    
            subprocess.run(["sudo", "mkfs.ntfs", "-f", files_partition, "-L", "COMET_FILES"], check=True)

        elif bios_type == "legacy":
            # Create new partition table and partition
            subprocess.run(["sudo", "parted", "-s", disk, "mklabel", "msdos"], check=True)
            subprocess.run(["sudo", "parted", "-s", disk, "mkpart", "primary", "0%", "100%"], check=True)
            partition = glob.glob(disk + "?")

            files_partition = partition[0] # Only one partition is here same for installation and boot files.

            # Refreshing the partitions
            subprocess.run(["sudo", "partprobe", disk], check=True)
            subprocess.run(["sudo", "udevadm", "settle"], check=True)

            # Creating the filesystems
            print(f"\n[*] Creating filesystems ...")
               
            subprocess.run(["sudo", "mkfs.ntfs", "-f", files_partition, "-L", "COMET"], check=True)
            subprocess.run(["sudo", "parted", "-s", disk, "set", "1", "boot", "on"], check=True) 

        print(f"[*] USB {disk} formatted successfully!\n")

    except subprocess.CalledProcessError:
        sys.exit("[*] Something went wrong, please retry.")
    
    if len(glob.glob(disk + "?")) == 2:
        return {"COMET_BOOT": boot_partition, "COMET_FILES": files_partition}
    else:
        return {"COMET": files_partition}



def unmount_usb(partitions):
    for part in partitions:
        print(f"Unmounting: {part}")
        result = subprocess.run(["sudo", "umount", "-f", part])
        

def mount_usb(partitions):

    for part_label in partitions.keys():
        print(f"Mounting: {partitions[part_label]} on /mnt/{part_label}")
        subprocess.run(["sudo", "mkdir", "-p", f"/mnt/{part_label}"])
        result = subprocess.run(["sudo", "mount", partitions[part_label], f"/mnt/{part_label}"])
        if result.returncode > 8:
            sys.exit(f"\n[*] Failed to mount {partitions[part_label]} on /mnt/{part_label}.\n[*] Please retry...")


def downloader(url, download_dir):
     
    with requests.get(url, stream = True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024 * 200 # 200KB chunk for smoother progress update.
        with open(f"{download_dir}{os.path.basename(url)}", "wb") as file, tqdm(
            total = total_size,
            unit = "B",
            unit_scale = True,
            unit_divisor = 1024,
            desc = f"{os.path.basename(url)}"
        ) as progress:
            for chunk in response.iter_content(chunk_size = chunk_size):
                download = file.write(chunk)
                progress.update(download)

def extractor(archive_path, extract_dir):
    
    with zf.ZipFile(archive_path, "r") as archive, tqdm(
        total = sum(file_info.file_size for file_info in archive.infolist()),
        unit = "B",
        unit_scale = True,
        unit_divisor = 1024,
        desc = f"Extracting {os.path.basename(archive_path)}"
    ) as progress:

        for file_info in archive.infolist():

            archive.extract(file_info, path = extract_dir)
            progress.update(file_info.file_size)




if __name__ == "__main__":
    main()
    