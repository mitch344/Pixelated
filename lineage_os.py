class LineageOS:

    fastboot_commands = [
        ("boot.img", "fastboot flash boot"),
        ("dtbo.img", "fastboot flash dtbo"),
        ("vendor_kernel_boot.img", "fastboot flash vendor_kernel_boot")
    ]

    additional_partitions = {
        "flame": {
            "device_name": "Pixel 4",
            "files": ["dtbo.img"]
        },
        "coral": {
            "device_name": "Pixel 4 XL",
            "files": ["dtbo.img"]
        },
        "sunfish": {
            "device_name": "Pixel 4a",
            "files": ["dtbo.img"]
        },
        "bramble": {
            "device_name": "Pixel 4a (5G)",
            "files": ["boot.img", "dtbo.img"]
        },
        "redfin": {
            "device_name": "Pixel 5",
            "files": ["boot.img", "dtbo.img"]
        },
        "barbet": {
            "device_name": "Pixel 5a (5G)",
            "files": ["boot.img", "dtbo.img"]
        },
        "oriole": {
            "device_name": "Pixel 6",
            "files": ["boot.img", "dtbo.img"]
        },
        "raven": {
            "device_name": "Pixel 6 Pro",
            "files": ["boot.img", "dtbo.img"]
        },
        "bluejay": {
            "device_name": "Pixel 6a",
            "files": ["boot.img", "dtbo.img"]
        },
        "panther": {
            "device_name": "Pixel 7",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        },
        "cheetah": {
            "device_name": "Pixel 7 Pro",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        },
        "lynx": {
            "device_name": "Pixel 7a",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        },
        "shiba": {
            "device_name": "Pixel 8",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        },
        "husky": {
            "device_name": "Pixel 8 Pro",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        },
        "felix": {
            "device_name": "Pixel Fold",
            "files": ["boot.img", "dtbo.img", "vendor_kernel_boot.img"]
        }
    }
