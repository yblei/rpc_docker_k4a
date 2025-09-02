# Setup instructions for Azure Kinect DK (No sudo required for regular use)

## One-time setup (requires sudo, but only once per system):

### 1. Add your user to the plugdev group:
```bash
sudo usermod -a -G plugdev $USER
```

### 2. Create udev rules for Azure Kinect:
```bash
sudo tee /etc/udev/rules.d/99-k4a.rules > /dev/null <<EOF
# Azure Kinect DK udev rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097a", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097b", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097c", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097d", MODE="0664", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097e", MODE="0664", GROUP="plugdev"
EOF
```

### 3. Reload udev rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. Log out and log back in (or reboot) to apply group changes

## Regular use (no sudo required):

After the one-time setup, you can use:
```bash
./run_kinect_safe.sh
```

## Alternative: Native installation (no Docker)

If you prefer to avoid Docker entirely, you can install directly on your system:

### Install packages:
```bash
# Add Microsoft repository (Ubuntu 18.04/20.04)
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository 'deb https://packages.microsoft.com/ubuntu/18.04/prod bionic main'

# Install Azure Kinect SDK
sudo apt update
sudo apt install libk4a1.4 libk4a1.4-dev k4a-tools

# Install Python packages
pip3 install pyk4a imageio numpy
```

This way, you only need sudo for the initial setup, and then it works for all users without elevated privileges.
