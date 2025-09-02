# Azure Kinect DK Dockerfile (Ubuntu 18.04)
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies including OpenGL libraries
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common python3 python3-pip python3-dev \
                       build-essential cmake pkg-config libusb-1.0-0 libusb-1.0-0-dev \
                       zlib1g-dev libjpeg-dev libpng-dev libtiff-dev \
                       udev libudev-dev libgl1 libglu1-mesa libgl1-mesa-glx libglib2.0-0 \
                       libxcb1 libxcb-shm0 libxcb-xfixes0 && \
    rm -rf /var/lib/apt/lists/*

# Add Microsoft package repository for Ubuntu 18.04
RUN wget -qO - https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    apt-add-repository 'deb https://packages.microsoft.com/ubuntu/18.04/prod bionic main'

# Install Azure Kinect SDK and tools with explicit depth engine verification
RUN echo 'libk4a1.4 libk4a1.4/accepted-eula-hash string 0f5d5c5de396e4fee4c0753a21fee0c1ed726cf0316204edda484f08cb266d76' | debconf-set-selections && \
    echo 'libk4a1.4 libk4a1.4/accept-eula boolean true' | debconf-set-selections && \
    apt-get update && \
    apt-get install -y libk4a1.4 libk4a1.4-dev k4a-tools && \
    rm -rf /var/lib/apt/lists/* && \
    echo "=== Fixing depth engine library path ===" && \
    ln -sf /usr/lib/x86_64-linux-gnu/libk4a1.4/libdepthengine.so.2.0 /usr/lib/x86_64-linux-gnu/libdepthengine.so.2.0 && \
    ldconfig && \
    echo "=== Verifying depth engine installation ===" && \
    ldconfig -p | grep depthengine && \
    find /usr -name "*depthengine*" 2>/dev/null

# Create script to set USB buffer size at container startup
RUN echo '#!/bin/bash' > /usr/local/bin/setup-usb.sh && \
    echo 'echo "Setting USB buffer size inside container..."' >> /usr/local/bin/setup-usb.sh && \
    echo 'if [ -w /sys/module/usbcore/parameters/usbfs_memory_mb ]; then' >> /usr/local/bin/setup-usb.sh && \
    echo '    echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb' >> /usr/local/bin/setup-usb.sh && \
    echo '    echo "USB buffer set to $(cat /sys/module/usbcore/parameters/usbfs_memory_mb)MB"' >> /usr/local/bin/setup-usb.sh && \
    echo 'else' >> /usr/local/bin/setup-usb.sh && \
    echo '    echo "USB buffer already set to $(cat /sys/module/usbcore/parameters/usbfs_memory_mb)MB (from host)"' >> /usr/local/bin/setup-usb.sh && \
    echo 'fi' >> /usr/local/bin/setup-usb.sh && \
    chmod +x /usr/local/bin/setup-usb.sh

# Install Python wrapper
RUN pip3 install numpy typing_extensions && \
    pip3 install pyk4a imageio

WORKDIR /workspace

# Create entrypoint script that sets up USB and runs the command
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo '/usr/local/bin/setup-usb.sh' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
