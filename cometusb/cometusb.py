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


def main() -> None:
    parser = argparse.ArgumentParser(
                    prog= "CometUSB.",
                    description="Create linux bootable USB."
                    )
    parser.add_argument("-l", "--list-os", action="store_true", help="Shows list of the available Operating Systems.")
    parser.add_argument("-o", "--operating-system", help="Name of the Operating System.")
    parser.add_argument("-b","--bios-type", help="BIOS type (e.g., UEFI or Legacy), check what your TARGET SYSTEM supports.")
    args = parser.parse_args()

    # List of available Opereating System
    OS = ["linuxmint"]

    # Shows list of available Operating Systems.
    if args.list_os:
        for number in range(len(OS)):
            print(number + 1, OS[number], sep=". ")
        sys.exit() # Exits after showing the OS list
    operating_system = Operating_System(args.operating_system.lower(), args.bios_type.lower())
    print(operating_system)
    operating_system.create()
    
class Operating_System():
    """
    This is the main object that contains all the information of the Operating System, target device and it's partition, bios-type etc.
    Once the create method is invoked it will start the process which includes wiping and formatting the target disk, downloading and extracting of files and
    applying bootloader.
    """
    def __init__(self, name: str, bios_type: str):
        self.name = name
        self._path_url = f"https://github.com/CometUSB/CometUSB/releases/download/{self.name}/"
        self.disk_size_reqd = self.name
        self.bios_type = bios_type
        self.partition_style = self.bios_type
        self.target_disk = get_disk_details()
        self.disk_partitions = format_disk(self.target_disk, self.bios_type, self.disk_size_reqd) # Dictionary of newly created partitions with labels
        self.files = self.name
        self._architecture= "64 Bit"


    def __str__(self) -> str:
        return f"\nOS = {self.name.upper()}\nArchitecture = {self._architecture}\nTarget System BIOS Type = {self.bios_type}\nTarget Device = {self.target_disk}\nPartition Style = {self.partition_style.upper()}\nFiles to be Downloaded = {[name for name in self.files.keys()]}\n"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets name of the Operating System.

        :param name: Name of the Operating System.
        :type name: str
        """
        OS: list = ["linuxmint"]
        if name not in OS:
            sys.exit("[!] Invalid or Unsupported Operating System.\nEnter 'cometusb.py --OS-list' without quotes to see the supported list of Operating systems")

        self._name: str = name

    @property
    def partition_style(self) -> str:
        return self._partition_style

    @partition_style.setter
    def partition_style(self, bios_type: str) -> None:
        """
        Sets the partition style i.e, MBR or GPT.

        :param bios_type: BIOS firmare type i.e, UEFI or Legacy.
        :type bios_type: str
        """
        if bios_type == "uefi":
            self._partition_style: str = "GPT"

        else:
            self._partition_style: str = "MBR"


    @property
    def bios_type(self) -> str:
        return self._bios_type
    @bios_type.setter
    def bios_type(self, bios_type: str) -> None:
        """
        Sets the BIOS type.

        :param bios_type: BIOS firmare type i.e, UEFI or Legacy.
        :type bios_type: str
        """
        if bios_type in ["uefi", "legacy"]:
            self._bios_type: str = bios_type

        else:
            sys.exit("[!] Invalid BIOS type.")

    @property
    def files(self) -> dict:
        return self._files

    @files.setter
    def files(self, name: str) -> None:
        """
        Selects files of given Operating System for Installation.

        :param name: Name of the Operating System.
        :type name: str
        """
        if len(self.disk_partitions) == 2:
            self._boot_partition, self._file_partition = self.disk_partitions.keys()
        elif len(self.disk_partitions) == 1:
            self._file_partition: str = [partition for partition in self.disk_partitions.keys()][0] # files_partition and boot_partition are the labels of boot partition and files partitions
            self._boot_partition: str = self._file_partition

        # Contains OS name and it's corresponding files and it's download path.
        OS_FILES: dict = {
        "linuxmint": {
            "boot.zip": f"/mnt/{self._boot_partition}/",
            "directories.zip":f"/mnt/{self._file_partition}/",
            "filesystem.squashfs.aa": f"/mnt/{self._file_partition}/",
            "filesystem.squashfs.ab": f"/mnt/{self._file_partition}/"
        }
        }

        self._files: dict = OS_FILES[name]

    @property
    def disk_size_reqd(self):
        return self._disk_size_reqd
    @disk_size_reqd.setter
    def disk_size_reqd(self, name):
        """
        Calculates the size of disk required for process.

        :param name: Name of the Operating System.
        """
        OS_FILES = {
            "linuxmint": [
                "boot.zip",
                "directories.zip",
                "filesystem.squashfs.aa",
                "filesystem.squashfs.ab"
            ]
        }

        total_size: int = 0
        for filename in OS_FILES[name]:
            with requests.get(self._path_url + filename, stream = True) as response:
                response.raise_for_status()
                total_size += int(response.headers.get("content-length", 0))

        total_size = total_size / (1024 * 1024 * 1024) # Total files size.

        USB_SIZES = [4, 8, 16, 32, 64]
        for usb_size in USB_SIZES:
            if usb_size / (total_size * 2) > 1: # Divided by twice of the total_size because of merging of OS images will require space for merged file. Although splitted image files will be removed.
                self._disk_size_reqd = usb_size
                break

    @property
    def target_disk(self) -> str:
        return self._target_disk

    @target_disk.setter
    def target_disk(self, target_disk: str) -> None:
        """
        Sets the target disk.

        :param target_disk: Name of the target disk.
        :type target_disk: str
        """
        self._target_disk: str = target_disk

    @property
    def disk_partitions(self) -> dict:
        return self._disk_partitions

    @disk_partitions.setter
    def disk_partitions(self, partitions: dict) -> None:
        """
        Sets partitions with of the target disk.

        :param partitions: Dictionary of all the newly created partition of target disk with corresponding labels.
        :type partitions: dict
        """
        self._disk_partitions: dict = partitions

    def bootloader(self) -> None:
        """
        Applies bootloader to the partition of the target disk containing boot files.
        """
        print(f"Applying bootloader on {self.target_disk} for {self.bios_type} systems...")
        if self.bios_type == "uefi":
            subprocess.run(["sudo", "grub-install" ,"--target=x86_64-efi", f"--efi-directory=/mnt/{self._boot_partition}", f"--boot-directory=/mnt/{self._boot_partition}/boot", "--removable"])

        else: 
            subprocess.run(["sudo", "grub-install" ,"--target=i386-pc", f"--boot-directory=/mnt/{self._boot_partition}/boot", f"{self.target_disk}"])

    def create(self) -> None:
        """
        This method calls all the required functions in sequence to perform the necessary operations to make the bootable media.
        """
        # Mounting newly created partitions.
        mount_usb(self.disk_partitions)

        # Disk configuration info. 
        print(f"\n[*] Disk {self.target_disk} configuration.")
        subprocess.run(["lsblk", self.target_disk, "-o", "NAME,SIZE,FSTYPE,FSVER,LABEL,MOUNTPOINTS"])

        for filename, download_dir in self.files.items():
            print() #To create gap between progress bars.
            print(f"Downloading {filename} into {download_dir}")
            downloader(self._path_url + filename, download_dir)
            print() #To create gap between progress bars.
            if filename.endswith(".zip"):
                # Extracting to create the directory tree structure
                extractor(download_dir + filename, download_dir)
                print() #To create gap between progress bars.
                os.remove(download_dir + filename) # Removing the zip file after extracting to free space in the USB.
            if filename.endswith(".aa"):
                image_name, download_dir = filename.rstrip(".aa"), download_dir
        print(f"[*] Making OS Image {image_name} ready for installation.\n[*] This may take a while depending upon your removable disk {self.target_disk}.")
        subprocess.run(f"sudo cat {download_dir}{image_name}.* > {download_dir}casper/{image_name}", shell=True, stdout=subprocess.DEVNULL)

        print("[*] Cleaning unnecessary file...")
        for splitted_image_file in glob.glob(f"{download_dir}{image_name}.*"):
            os.remove(splitted_image_file)

        # Applying bootloader
        self.bootloader()

        print("Media created succesfully\nNOTE: Linux disk sometimes is not detected in BIOS, try disabling secure boot of your BIOS if facing any issues while booting.")

def get_disk_details() -> str:
    """
    Executes the 'lsblk' command to retrieve detailed information for physical
    block disks using JSON output for robust, programmatic parsing.

    :return: A string of target device.
    :rtype: str
    """

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

def format_disk(disk: str, bios_type: str, size: int) -> str:
    """
    Formats the target disk, converts it into GPT or MBR then create partitions and filesystems compatible for the given BIOS Type i.e, UEFI or Legacy. 

    :param disk: Name of target disk. 
    :type disk: str
    :param bios_type: BIOS firmware type.
    :type bios_type: str
    :param size: Size of the target disk required.
    :return: Dictionary of all the partition of target disk with corresponding labels.
    :rtype: str
    """
     # Confirming to Format the USB
    print(f"\n[!] MINIMUM {size} GB Disk is required.\n[*] This will ERASE all data on {disk}") 
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
            subprocess.run(["sudo", "parted", "-s", disk, "mkpart", "primary", "1MiB", "501MiB"], check=True)
            partition = glob.glob(disk + "?")
            boot_partition = partition[0]
            subprocess.run(["sudo", "parted", "-s", disk, "mkpart", "primary", "501MiB", "100%"], check=True)
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

def unmount_usb(partitions: list) -> None:
    """
    Unmounts all the existing partitions of the target disk to intitate the formatting process by format_disk function.
    
    :param partitions: List of all the partitions in the target disk.
    :type partitions: list
    """

    for part in partitions:
        print(f"Unmounting: {part}")
        subprocess.run(["sudo", "umount", "-f", part])
        
def mount_usb(partitions: dict) -> None:
    """
    Mounts all the newly created partitions of the target disk by format_disk function.

    :param partitions: Dictionary of all the newly created partition of target disk with corresponding labels.
    :type partitions: dict
    """
    for part_label in partitions.keys():
        print(f"Mounting: {partitions[part_label]} on /mnt/{part_label}")
        subprocess.run(["sudo", "mkdir", "-p", f"/mnt/{part_label}"])
        result = subprocess.run(["sudo", "mount", partitions[part_label], f"/mnt/{part_label}"])
        if result.returncode > 8:
            sys.exit(f"\n[*] Failed to mount {partitions[part_label]} on /mnt/{part_label}.\n[*] Please retry...")

def downloader(url: str, download_dir: str) -> None:
    """
    Downloads all the files from github release page of the corresponding operating system of the CometUSB organization.

    :param url: Download URL of individual files.
    :type url: str
    :param download_dir: Download location of the given files.
    :type download_dir: str
    """
    with requests.get(url, stream = True) as response:
        response.raise_for_status()
        total_size: int = int(response.headers.get("content-length", 0))
        chunk_size: int = 1024 * 200 # 200KB chunk for smoother progress update.
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

def extractor(archive_path: str, extract_dir: str) -> None:
    """
    Extracts the compressed archive to given location.

    :param archive_path: Complete path of the compressed archives.
    :type archive_path: str
    :param extract_dir: Extract folder for the corresponding archive.
    :type extract_dir: str
    """
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
    