#!/bin/bash

echo "Installing Azure Kinect DK support natively on Ubuntu..."

# Check if we're on a supported Ubuntu version
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "This script is designed for Ubuntu. Manual installation may be needed for other distributions."
    exit 1
fi

# Add Microsoft repository
echo "Adding Microsoft repository..."
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository 'deb https://packages.microsoft.com/ubuntu/18.04/prod bionic main'

# Accept EULA non-interactively
echo 'libk4a1.4 libk4a1.4/accepted-eula-hash string 0f5d5c5de396e4fee4c0753a21fee0c1ed726cf0316204edda484f08cb266d76' | sudo debconf-set-selections
echo 'libk4a1.4 libk4a1.4/accept-eula boolean true' | sudo debconf-set-selections

# Install Azure Kinect SDK
echo "Installing Azure Kinect SDK..."
sudo apt update
sudo apt install -y libk4a1.4 libk4a1.4-dev k4a-tools

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user pyk4a imageio numpy

# Set up udev rules for non-root access
echo "Setting up udev rules..."
sudo tee /etc/udev/rules.d/99-k4a.rules > /dev/null <<EOF
# Azure Kinect DK udev rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097a", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097b", MODE="0666", GROUP="plugdev" 
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097d", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097e", MODE="0666", GROUP="plugdev"
EOF

# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "✅ Installation complete!"
echo ""
echo "⚠️  IMPORTANT: You need to log out and log back in (or reboot) for the group changes to take effect."
echo ""
echo "After logging back in, test with:"
echo "  k4arecorder --list"
echo "  python3 working_test.py"
