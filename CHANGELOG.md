# Changelog

All notable changes to the RPC Docker K4A project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-02

### Added
- Complete Python package structure with `rpc_docker_k4a` module
- XML-RPC server (`AzureKinectRPCServer`) with full PyK4A functionality
- XML-RPC client (`AzureKinectRPCClient`) with display, save, and info modes
- Command-line tools: `k4a-rpc-server` and `k4a-rpc-client`
- Utility functions for image processing and configuration validation
- Docker integration with NVIDIA OpenGL and Mesa software rendering
- Multi-language RPC support (Python, JavaScript, cURL examples)
- Professional packaging with pyproject.toml and setuptools
- Comprehensive documentation and usage examples
- MIT License
- Git ignore rules for captured images
- USB device rules for Azure Kinect access

### Features
- Remote Azure Kinect access via XML-RPC over network
- Base64 image encoding for network transfer
- Multiple image formats: BGR, RGB, JPEG, PNG, RAW, NORMALIZED, COLORMAP
- Auto-capture mode with background threading
- Device configuration management
- Error handling and logging
- Simulation mode for testing without hardware
- VPN-compatible Docker networking

### Docker Solutions
- **NVIDIA OpenGL**: Hardware-accelerated containers with GPU support
- **Mesa Software**: Universal compatibility containers for any system
- Automatic EULA acceptance for Microsoft packages
- Complete USB device access and permissions
- X11 forwarding support for GUI applications

### API Methods
- `device_connect()`, `device_start()`, `device_stop()`, `device_disconnect()`
- `get_capture()`, `get_color_image()`, `get_depth_image()`, `get_ir_image()`
- `start_auto_capture()`, `stop_auto_capture()`, `get_latest_capture()`
- `get_device_info()` for status and capabilities

### Technical Specifications
- Python 3.8+ compatibility
- Dependencies: numpy>=1.20.0, opencv-python>=4.5.0, pyk4a>=1.4.0
- XML-RPC protocol for multi-language support
- Thread-safe operation with locking mechanisms
- Comprehensive error handling and status reporting

### Documentation
- Complete README with installation and usage instructions
- RPC API reference with all methods and parameters
- Multi-language client examples
- Docker deployment guides
- Troubleshooting section
- Performance optimization tips
