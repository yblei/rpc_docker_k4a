# RPC Docker K4A - New Implementation Guide

## 🚀 Overview

The `RpcDockerK4a` class has been completely redesigned to provide seamless Azure Kinect access without requiring any host system dependencies. The implementation assumes **PyK4A is never installed on the host system** and instead automatically manages Docker containers for you.

## 🎯 Key Features

- **Zero Host Dependencies**: No need for PyK4A, libk4a, or Azure Kinect SDK on host
- **Automatic Hardware Detection**: Detects NVIDIA Container Toolkit for acceleration
- **Automatic Container Building**: Builds appropriate Docker containers on first use
- **Seamless Lifecycle Management**: Handles container startup, cleanup, and error recovery
- **Production Ready**: Robust error handling and graceful fallbacks

## 🧠 Detection Logic

### 1. Hardware Acceleration Detection
```python
# Checks for NVIDIA Container Toolkit
nvidia_available = k4a._check_nvidia_container_toolkit()
```

**Detection Methods:**
- Look for `nvidia-container-runtime` binary in PATH
- Check Docker daemon info for NVIDIA runtime support
- Verify Docker can use `--runtime=nvidia` flag

### 2. Container Selection Strategy

| NVIDIA Toolkit | Container Used | Acceleration |
|----------------|----------------|--------------|
| ✅ Available | `azure-kinect-prebuilt-vpn` | Hardware (OpenGL) |
| ❌ Missing | `azure-kinect-mesa-vpn` | Software (Mesa) |

### 3. Automatic Building

If the required container doesn't exist:
1. Locate appropriate build script (`build-prebuilt-vpn.sh` or `build-mesa-vpn.sh`)
2. Execute build script with proper environment
3. Verify successful build completion
4. Use newly built container

## 📋 Usage Patterns

### Pattern 1: Automatic (Recommended)
```python
from rpc_docker_k4a import RpcDockerK4a

# System automatically:
# - Detects NVIDIA Container Toolkit
# - Builds appropriate container if missing
# - Starts RPC server in container
# - Provides client interface
with RpcDockerK4a() as k4a:
    devices = k4a.device_get_installed_count()
    if devices > 0:
        k4a.connect_and_start()
        k4a.capture_and_save(count=10)
```

### Pattern 2: Force Container Type
```python
# Force NVIDIA container (will build if missing)
k4a = RpcDockerK4a(use_docker='nvidia', verbose=True)

# Force Mesa container (will build if missing)  
k4a = RpcDockerK4a(use_docker='mesa', verbose=True)

try:
    devices = k4a.device_get_installed_count()
finally:
    k4a.close()
```

### Pattern 3: Manual Building
```python
# Build containers without starting server
k4a = RpcDockerK4a(auto_start=False, verbose=True)

# Build best available container
image_name = k4a.build_image('auto')
print(f"Built: {image_name}")

# Build specific container types
nvidia_image = k4a.build_image('nvidia')
mesa_image = k4a.build_image('mesa')
```

### Pattern 4: Production Usage
```python
class AzureKinectService:
    def __init__(self):
        self.k4a = None
    
    def start(self):
        try:
            self.k4a = RpcDockerK4a(
                verbose=False,    # Quiet in production
                timeout=120,      # Allow container building time
                auto_build=True   # Build if needed
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start Azure Kinect: {e}")
            return False
    
    def capture_frame(self):
        if not self.k4a:
            return None
        return self.k4a.get_capture()
    
    def stop(self):
        if self.k4a:
            self.k4a.close()
            self.k4a = None
```

## ⚙️ Configuration Options

### Constructor Parameters

```python
RpcDockerK4a(
    port=None,              # Auto-find available port
    host='localhost',       # Server bind address
    timeout=60.0,          # Connection timeout (increased for building)
    use_docker='auto',     # 'auto', 'nvidia', 'mesa'
    docker_image='auto',   # 'auto' or specific image name
    verbose=False,         # Enable detailed output
    auto_start=True,       # Start server on init
    auto_build=True        # Build images if missing
)
```

### Docker Strategies

| Strategy | Behavior |
|----------|----------|
| `'auto'` | Auto-detect best container, build if needed |
| `'nvidia'` | Force NVIDIA container, build if needed |
| `'mesa'` | Force Mesa container, build if needed |

### Image Selection

| Image Setting | Behavior |
|---------------|----------|
| `'auto'` | Auto-select based on hardware |
| `'azure-kinect-prebuilt-vpn'` | Use specific NVIDIA image |
| `'azure-kinect-mesa-vpn'` | Use specific Mesa image |
| Custom name | Use custom image name |

## 🏗️ Build Scripts

The system automatically locates and uses these build scripts:

```bash
rpc_docker_k4a/docker/
├── build-prebuilt-vpn.sh    # Build NVIDIA hardware-accelerated container
├── build-mesa-vpn.sh        # Build Mesa software-rendering container
├── deploy-prebuilt-vpn.sh   # Deploy NVIDIA container
└── deploy-mesa-vpn.sh       # Deploy Mesa container
```

## 📊 System Information

Get detailed information about the running system:

```python
with RpcDockerK4a() as k4a:
    info = k4a.get_server_info()
    print(f"NVIDIA Toolkit: {info['nvidia_toolkit_available']}")
    print(f"Container ID: {info.get('container_id', 'N/A')}")
    print(f"Docker Mode: {info['docker_mode']}")
    print(f"Using Docker: {info['using_docker']}")
```

## 🛠️ Command Line Interface

### Basic Usage
```bash
# Auto-detect and start (builds container if needed)
python3 -m rpc_docker_k4a.combined --verbose

# Force specific container type
python3 -m rpc_docker_k4a.combined --docker nvidia --verbose
python3 -m rpc_docker_k4a.combined --docker mesa --verbose

# Build container without starting server
python3 -m rpc_docker_k4a.combined --build-only --docker auto --verbose
```

### CLI Options
```
--port PORT              Server port (auto-detect if not specified)
--host HOST              Server host address  
--timeout TIMEOUT        Connection timeout in seconds
--docker {auto,nvidia,mesa}  Docker image type strategy
--image IMAGE            Specific Docker image name
--verbose                Enable detailed output
--no-auto-start          Don't automatically start server
--no-auto-build          Don't automatically build missing images
--build-only             Only build image, don't start server
```

## 🚨 Error Handling

The system provides robust error handling:

### Missing Docker
```
RuntimeError: Docker is not available. This tool requires Docker to run PyK4A.
```

### Container Build Failure
```
RuntimeError: Failed to build nvidia image: Build script failed
```

### Build Script Missing
```
RuntimeError: Build script 'build-prebuilt-vpn.sh' not found
```

### Automatic Fallbacks

1. **NVIDIA → Mesa**: If NVIDIA Container Toolkit missing, falls back to Mesa
2. **Auto-build**: If `auto_build=False` and image missing, shows build instructions
3. **Timeout**: Increases timeout automatically for container building operations

## 🎉 Benefits

### For Developers
- **Zero Setup**: No PyK4A installation required
- **Automatic**: Everything handled automatically
- **Flexible**: Force specific configurations when needed
- **Debuggable**: Verbose output shows exactly what's happening

### For Production
- **Reliable**: Consistent environment across all deployments
- **Scalable**: Container-based architecture
- **Maintainable**: Automatic dependency management
- **Portable**: Runs on any Docker-capable system

### For DevOps
- **Containerized**: Standard Docker deployment patterns
- **Accelerated**: Hardware acceleration when available
- **Fallback**: Software rendering when hardware unavailable
- **Monitored**: Comprehensive logging and status information

## 📈 Migration from Old Version

### Before (Manual Container Management)
```python
# Had to manually build containers:
# ./build-prebuilt-vpn.sh

# Had to manually manage server:
server = subprocess.Popen(['kinect_rpc_server.py'])
client = AzureKinectRPCClient()
# Manual cleanup required
```

### After (Automatic Management)
```python
# Everything automatic:
with RpcDockerK4a() as k4a:  # Detects, builds, starts, cleans up
    devices = k4a.device_get_installed_count()
# Automatic cleanup on exit
```

## 🔍 Troubleshooting

### Enable Verbose Mode
```python
with RpcDockerK4a(verbose=True) as k4a:
    # Detailed output shows:
    # - Hardware detection results
    # - Container selection logic
    # - Build progress (if needed)
    # - Server startup status
```

### Check System Status
```python
k4a = RpcDockerK4a(auto_start=False)
info = k4a.get_server_info()
print(f"NVIDIA Available: {info['nvidia_toolkit_available']}")
print(f"Docker Available: {k4a._check_docker_available()}")
```

### Manual Container Building
```bash
# Build containers manually if needed
./rpc_docker_k4a/docker/build-prebuilt-vpn.sh  # NVIDIA
./rpc_docker_k4a/docker/build-mesa-vpn.sh      # Mesa
```

This new implementation provides a seamless, production-ready solution for Azure Kinect access without any host system dependencies!
