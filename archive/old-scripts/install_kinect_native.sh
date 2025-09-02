#!/bin/bash

echo "Installing Azure Kinect SDK natively to fix depth engine error 204..."

# Add Microsoft package repository
if ! grep -q "packages.microsoft.com" /etc/apt/sources.list.d/microsoft-prod.list 2>/dev/null; then
    echo "Adding Microsoft repository..."
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
    sudo apt-add-repository https://apt.repos.microsoft.com/ubuntu/18.04/prod
    sudo apt update
fi

# Install Azure Kinect SDK
echo "Installing Azure Kinect SDK..."
sudo apt install -y libk4a1.4-dev libk4a1.4 k4a-tools

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user pyk4a numpy opencv-python imageio

# Set up udev rules for non-root access
echo "Setting up udev rules for Azure Kinect..."
sudo tee /etc/udev/rules.d/99-k4a.rules > /dev/null <<EOF
# Azure Kinect DK
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097a", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097b", MODE="0666", GROUP="plugdev"  
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097d", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="097e", MODE="0666", GROUP="plugdev"
EOF

# Reload udev rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Add user to plugdev group
sudo usermod -a -G plugdev $USER

echo "Native installation complete!"
echo "You may need to log out and log back in for group changes to take effect."
echo "Or run: newgrp plugdev"
