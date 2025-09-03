# RPC Docker K4A - Production Ready

🎯 **Production-ready Azure Kinect SDK with integrated Docker support and SSH compatibility.**

## Features

✅ **SSH Compatible**: Works perfectly over SSH connections  
✅ **Integrated Virtual Display**: Built-in Xvfb in Docker container  
✅ **NVIDIA GPU Acceleration**: Automatic GPU detection and acceleration  
✅ **Error 207 Solved**: OpenGL context creation works in containerized environments  
✅ **Automatic Container Management**: Docker lifecycle handled automatically  
✅ **Full Depth + Color Access**: Complete Azure Kinect functionality  

## Quick Start

```python
from rpc_docker_k4a.combined import RpcDockerK4a

# Works perfectly over SSH!
with RpcDockerK4a(use_docker='nvidia', verbose=True) as k4a:
    config = {
        'color_resolution': '1080P',
        'depth_mode': 'NFOV_2X2BINNED',
        'camera_fps': 15,
        'synchronized_images_only': True
    }
    
    k4a.server.device_connect(config)
    k4a.server.device_start()
    k4a.server.get_capture(10000)
    
    # Get depth image (colorized)
    depth_result = k4a.server.get_depth_image('COLORMAP', 0, 4000)
    
    # Get color image  
    color_result = k4a.server.get_color_image('BGR', 90)
```

## Installation

```bash
# Clone repository
git clone https://github.com/yblei/rpc_docker_k4a.git
cd rpc_docker_k4a

# Install package
pip install -e .

# Run demo
python azure_kinect_demo.py
```

## Demo

The included demo captures synchronized depth and color images:

```bash
python azure_kinect_demo.py
```

**Sample Output:**
```
🎯 Azure Kinect SSH Demo - Final Solution
==================================================
✅ Works over SSH
✅ Integrated virtual display in container
✅ NVIDIA GPU acceleration
✅ Full depth + color camera access

📸 Capturing synchronized depth + color frames...
📷 Frame 1/3:
   ✅ Capture successful
   📊 Color shape: [1080, 1920, 4]
   📊 Depth shape: [288, 320]
   💾 Depth saved: examples/demo_depth_01.jpg
   💾 Color saved: examples/demo_color_01.jpg

🎉 DEMO SUCCESSFUL!
✅ Azure Kinect depth camera working over SSH
✅ Error 207 completely resolved
```

## Technical Solution

The package solves the common **Error 207** (OpenGL context creation failed) that occurs when using Azure Kinect over SSH:

### The Problem
- Azure Kinect depth engine requires OpenGL 4.4+ context
- SSH connections don't provide GPU/OpenGL access
- Docker container isolation prevents OpenGL context creation
- Results in "Error 207: depth engine initialization failed"

### The Solution
1. **Integrated Xvfb**: Virtual display runs inside Docker container
2. **NVIDIA GPU Acceleration**: Hardware acceleration through NVIDIA runtime  
3. **OpenGL 4.5 Support**: Mesa + NVIDIA provides required OpenGL context
4. **Automatic Management**: Container lifecycle handled by Python class

### Container Features
- **Built-in Virtual Display**: No external Xvfb dependency
- **Startup Script**: `/usr/local/bin/start-with-xvfb.sh` manages display
- **Environment Variables**: Proper OpenGL/NVIDIA configuration
- **Hardware Access**: USB device access for Azure Kinect

## API

### Basic Usage
```python
from rpc_docker_k4a.combined import RpcDockerK4a

# Initialize with automatic hardware detection
k4a = RpcDockerK4a(use_docker='auto', verbose=True)

# Manual container selection
k4a = RpcDockerK4a(use_docker='nvidia')  # Force NVIDIA
k4a = RpcDockerK4a(use_docker='mesa')    # Force Mesa

# Context manager (recommended)
with RpcDockerK4a() as k4a:
    # Your code here
    pass
```

### Image Capture
```python
with RpcDockerK4a() as k4a:
    # Configure device
    config = {
        'color_resolution': '1080P',      # 720P, 1080P, 1440P, 2160P, 3072P
        'depth_mode': 'NFOV_2X2BINNED',  # NFOV_UNBINNED, NFOV_2X2BINNED, WFOV_*
        'camera_fps': 15,                # 5, 15, 30 FPS
        'synchronized_images_only': True  # Sync depth + color
    }
    
    # Connect and start
    k4a.server.device_connect(config)
    k4a.server.device_start()
    
    # Capture frame
    k4a.server.get_capture(timeout_ms=10000)
    
    # Get images
    depth = k4a.server.get_depth_image('COLORMAP', 0, 4000)  # Colorized depth
    color = k4a.server.get_color_image('BGR', 90)            # Color image
```

## Docker Images

Two container types are automatically built:

### NVIDIA Container (`azure-kinect-prebuilt-vpn`)
- **Base**: `nvidia/opengl:1.2-glvnd-devel-ubuntu22.04`
- **Features**: GPU-accelerated, integrated Xvfb, NVIDIA runtime
- **Requirements**: NVIDIA GPU + Container Toolkit
- **Performance**: Hardware OpenGL acceleration

### Mesa Container (`azure-kinect-mesa-vpn`) 
- **Base**: `ubuntu:22.04` 
- **Features**: Software rendering, integrated Xvfb
- **Requirements**: Any x86_64 system with Docker
- **Performance**: CPU-based OpenGL (slower)

## Requirements

- **Docker** with NVIDIA Container Toolkit (recommended)
- **Azure Kinect DK** hardware
- **USB 3.0** connection
- **Linux** host system
- **Python 3.8+**

## Files Structure

```
rpc_docker_k4a/
├── rpc_docker_k4a/           # Main package
│   ├── combined.py           # Main RpcDockerK4a class
│   ├── client.py            # RPC client
│   ├── server.py            # RPC server
│   └── docker/              # Docker configuration
│       ├── Dockerfile.k4a-prebuilt  # NVIDIA container
│       ├── Dockerfile.mesa          # Mesa container
│       └── build-*.sh              # Build scripts
├── azure_kinect_demo.py     # Production demo
├── examples/                # Example captures
├── README.md               # This file
└── pyproject.toml          # Package configuration
```

## License

MIT License - see LICENSE file.
