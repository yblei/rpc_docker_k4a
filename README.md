# RPC Docker K4A - Azure Kinect Remote Procedure Call Package

A comprehensive Python package for Azure Kinect sensor access through Docker containers with XML-RPC server capabilities for remote depth sensing and image capture.

## 🎯 Key Features

- **XML-RPC Server**: Remote access to Azure Kinect functionality over network
- **Docker Integration**: NVIDIA OpenGL hardware acceleration + Mesa software fallback
- **Multi-Language Support**: XML-RPC compatible with Python, JavaScript, Java, C#, etc.
- **Complete API**: Full PyK4A functionality exposed via RPC
- **Production Ready**: Professional packaging with command-line tools

## 📦 Installation

### Install as Python Package
```bash
pip install rpc-docker-k4a
```

### Install from Source
```bash
git clone https://github.com/your-repo/rpc-docker-k4a
cd rpc-docker-k4a
pip install -e .
```

## 🚀 Quick Start

### Simple Usage (Recommended)
```python
from rpc_docker_k4a import RpcDockerK4a

# Automatically detects hardware and builds appropriate Docker container
with RpcDockerK4a() as k4a:
    # Connect to Azure Kinect device
    k4a.connect_and_start()
    
    # Capture and save images
    k4a.capture_and_save(count=5)
    
    # Server automatically stops when context exits
```

### Hardware Acceleration Auto-Detection
The package automatically detects your system capabilities:

- **NVIDIA Container Toolkit detected**: Uses hardware-accelerated OpenGL container
- **No NVIDIA Container Toolkit**: Falls back to Mesa software rendering container
- **Missing Docker images**: Automatically builds the appropriate container

### Integration in Your Projects
```python
from rpc_docker_k4a import RpcDockerK4a

class MyApplication:
    def __init__(self):
        # Azure Kinect automatically managed with optimal acceleration
        self.kinect = RpcDockerK4a(verbose=False)
    
    def process_depth_data(self):
        if self.kinect.connect_and_start():
            # Use XML-RPC interface for custom operations
            capture = self.kinect.server.get_capture(1000)
            depth_data = self.kinect.server.get_depth_image('RAW', 0, 4000)
            # Process your depth data here...
            self.kinect.cleanup()

# Usage
app = MyApplication()
app.process_depth_data()
# Server automatically stops when app is destroyed
```

### Manual Server/Client (Advanced)
```bash
# Start RPC server manually
k4a-rpc-server --host 0.0.0.0 --port 8000 --verbose

# Use client from another terminal/machine
k4a-rpc-client --host localhost --mode info
k4a-rpc-client --host localhost --mode save --count 5
```

## 🖥️ RPC Server Usage

### Command Line Interface

```bash
k4a-rpc-server [OPTIONS]

Options:
  --host HOST          Server host address (default: localhost)
  --port PORT          Server port (default: 8000)
  --verbose, -v        Enable verbose logging
  --help               Show help message
```

### Python API

```python
from rpc_docker_k4a import AzureKinectRPCServer
from xmlrpc.server import SimpleXMLRPCServer

# Create and configure server
server = SimpleXMLRPCServer(('0.0.0.0', 8000), allow_none=True)
kinect_service = AzureKinectRPCServer()
server.register_instance(kinect_service)

# Start server
print("Azure Kinect RPC Server starting on 0.0.0.0:8000")
server.serve_forever()
```

### Docker Deployment

```bash
# NVIDIA OpenGL version (hardware accelerated)
./rpc_docker_k4a/docker/deploy-prebuilt-vpn.sh k4a-rpc-server --host 0.0.0.0 --verbose

# Mesa version (universal compatibility)
./rpc_docker_k4a/docker/deploy-mesa-vpn.sh k4a-rpc-server --host 0.0.0.0 --verbose
```

### Automatic Docker Container Management

The `RpcDockerK4a` class automatically handles Docker container lifecycle:

```python
# Automatic hardware detection and container building
with RpcDockerK4a(verbose=True) as k4a:
    # First run: Detects NVIDIA Container Toolkit and builds appropriate image
    # Subsequent runs: Uses existing image
    device_count = k4a.device_get_installed_count()
```

**Container Selection Logic:**
- Checks for NVIDIA Container Toolkit installation
- If available: Builds/uses `azure-kinect-prebuilt-vpn` (hardware accelerated)  
- If not available: Builds/uses `azure-kinect-mesa-vpn` (software rendering)
- Missing images are automatically built on first use

**Manual Control:**
```python
# Force specific container type
k4a = RpcDockerK4a(use_docker='nvidia', verbose=True)  # Force NVIDIA
k4a = RpcDockerK4a(use_docker='mesa', verbose=True)    # Force Mesa
k4a = RpcDockerK4a(auto_build=False)                   # Disable auto-building

# Build containers manually
k4a.build_image('nvidia')  # Build NVIDIA image
k4a.build_image('mesa')    # Build Mesa image
k4a.build_image('auto')    # Build best available
```

## 📱 RPC Client Usage

### Command Line Interface

```bash
k4a-rpc-client [OPTIONS]

Options:
  --host HOST          Server host address (default: localhost)
  --port PORT          Server port (default: 8000)
  --mode MODE          Operation mode: display, save, info (default: display)
  --count COUNT        Number of images to save in save mode (default: 5)
  --help               Show help message
```

### Python API

```python
from rpc_docker_k4a import AzureKinectRPCClient

# Connect to server
client = AzureKinectRPCClient('192.168.1.100', 8000)

# Connect and start device
if client.connect_and_start():
    # Get device information
    client.get_device_status()
    
    # Capture and save images
    client.save_images(count=10)
    
    # Live display (requires display)
    client.capture_and_display()
    
    # Cleanup
    client.cleanup()
```

## 🌐 Multi-Language RPC Access

The XML-RPC server can be accessed from any language supporting XML-RPC:

### Python
```python
import xmlrpc.client

server = xmlrpc.client.ServerProxy('http://localhost:8000')
info = server.get_device_info()
print(f"Device connected: {info['connected']}")
```

### JavaScript (Node.js)
```javascript
const xmlrpc = require('xmlrpc');

const client = xmlrpc.createClient('http://localhost:8000');
client.methodCall('get_device_info', [], (err, data) => {
    console.log('Device info:', data);
});
```

### cURL
```bash
curl -X POST http://localhost:8000/RPC2 \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
      <methodCall>
        <methodName>get_device_info</methodName>
        <params></params>
      </methodCall>'
```

## 🔧 RPC API Reference

### Device Control
- `device_connect(config_dict)` - Connect to Azure Kinect with configuration
- `device_start()` - Start data streaming
- `device_stop()` - Stop streaming
- `device_disconnect()` - Disconnect device
- `get_device_info()` - Get device status and capabilities

### Image Capture
- `get_capture(timeout_ms)` - Single frame capture
- `get_color_image(format, quality)` - Get color image as base64
- `get_depth_image(format, min_depth, max_depth)` - Get depth image as base64
- `get_ir_image(format)` - Get IR image as base64

### Advanced Features
- `start_auto_capture(interval_ms)` - Background continuous capture
- `get_latest_capture()` - Get latest auto-captured frame
- `stop_auto_capture()` - Stop background capture

### Configuration Parameters
```python
config = {
    'color_resolution': '720P',  # 720P, 1080P, 1440P, 2160P
    'depth_mode': 'NFOV_UNBINNED',  # NFOV_UNBINNED, NFOV_2X2BINNED, WFOV_UNBINNED, WFOV_2X2BINNED
    'camera_fps': 30,  # 5, 15, 30
    'synchronized_images_only': True
}
```

## 🐳 Docker Solutions

### NVIDIA OpenGL (Hardware Accelerated)
```bash
# Build container
./rpc_docker_k4a/docker/build-prebuilt-vpn.sh

# Deploy RPC server
./rpc_docker_k4a/docker/deploy-prebuilt-vpn.sh k4a-rpc-server --host 0.0.0.0

# Interactive mode
./rpc_docker_k4a/docker/deploy-prebuilt-vpn.sh bash
```

### Mesa Software Rendering (Universal)
```bash
# Build container
./rpc_docker_k4a/docker/build-mesa-vpn.sh

# Deploy RPC server  
./rpc_docker_k4a/docker/deploy-mesa-vpn.sh k4a-rpc-server --host 0.0.0.0

# Interactive mode
./rpc_docker_k4a/docker/deploy-mesa-vpn.sh bash
```

## 💡 Usage Examples

### Remote Depth Sensing
```python
import xmlrpc.client
import base64
import numpy as np

# Connect to remote server
server = xmlrpc.client.ServerProxy('http://192.168.1.100:8000')

# Connect and start device
server.device_connect({
    'depth_mode': 'NFOV_UNBINNED',
    'color_resolution': '720P',
    'camera_fps': 30
})
server.device_start()

# Capture depth image
capture_result = server.get_capture(1000)
depth_result = server.get_depth_image('RAW', 0, 4000)

if depth_result['success']:
    # Decode raw depth data
    depth_data = base64.b64decode(depth_result['image_data'])
    depth_array = np.frombuffer(depth_data, dtype=np.uint16)
    depth_image = depth_array.reshape((576, 640))
    
    print(f"Depth range: {depth_image.min()}-{depth_image.max()}mm")

# Cleanup
server.device_disconnect()
```

### Automated Image Collection
```python
from rpc_docker_k4a import AzureKinectRPCClient
import time

client = AzureKinectRPCClient('localhost', 8000)

if client.connect_and_start():
    # Start auto-capture at 30fps
    result = client.server.start_auto_capture(33)  # 33ms = ~30fps
    
    # Collect images for 10 seconds
    for i in range(10):
        time.sleep(1)
        
        # Get latest capture
        latest = client.server.get_latest_capture()
        if latest['success']:
            # Save color image
            color_result = client.server.get_color_image('JPEG', 95)
            if color_result['success']:
                with open(f'frame_{i:03d}.jpg', 'wb') as f:
                    image_data = base64.b64decode(color_result['image_data'])
                    f.write(image_data)
    
    # Stop auto-capture
    client.server.stop_auto_capture()
    client.cleanup()
```

## 🔧 Device Setup

### USB Device Access
```bash
# Copy udev rules
sudo cp rpc_docker_k4a/99-k4a.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### X11 Display (for GUI applications)
```bash
# Allow X11 connections
xhost +local:docker

# Or for specific host
xhost +local:
```

## 📋 Requirements

### System Requirements
- Ubuntu 18.04+ or compatible Linux distribution
- USB 3.0 port for Azure Kinect device
- Python 3.8+

### For Hardware Acceleration
- NVIDIA GPU with drivers
- Docker with NVIDIA runtime (`nvidia-docker2`)

### Python Dependencies
- `numpy>=1.20.0`
- `opencv-python>=4.5.0`
- `pyk4a>=1.4.0`

## 🆘 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is available
netstat -ln | grep :8000

# Check pyk4a installation
python -c "import pyk4a; print('OK')"
```

**Client connection refused:**
```bash
# Test server connectivity
curl http://localhost:8000

# Check server logs for errors
k4a-rpc-server --verbose
```

**Device not detected:**
```bash
# Check USB connection
lsusb | grep Microsoft

# Verify udev rules
ls -la /etc/udev/rules.d/*k4a*

# Check permissions
ls -la /dev/bus/usb/
```

**Docker issues:**
```bash
# Check NVIDIA runtime
docker info | grep nvidia

# Test container access
./rpc_docker_k4a/docker/deploy-prebuilt-vpn.sh lsusb
```

### Performance Tips

- Use NVIDIA version for best performance
- Configure appropriate depth mode for your application
- Use auto-capture for continuous streaming
- Consider network latency for remote access

## 📖 API Documentation

### Image Formats
- **BGR/RGB**: Standard color formats
- **JPEG**: Compressed color format with quality setting
- **PNG**: Lossless compressed format
- **RAW**: Raw uint16 depth data
- **NORMALIZED**: 8-bit normalized depth
- **COLORMAP**: False-color depth visualization

### Response Format
All RPC methods return dictionaries with:
```python
{
    'success': bool,        # Operation success status
    'message': str,         # Human-readable message
    'data': any,           # Method-specific data
    # Additional fields depending on method
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- GitHub Issues: Report bugs and request features
- Documentation: Full API reference available
- Examples: Check `rpc_docker_k4a/examples.py` for more usage patterns
