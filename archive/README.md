# Archive Directory

This directory contains historical attempts and development files that led to the two working solutions.

## failed-attempts/
- `Dockerfile.k4a-source` - Failed attempt to compile Azure Kinect SDK from source (OpenSSL 3.0 compatibility issues)
- Various Ubuntu version attempts and GPU configurations that didn't work

## old-docs/
- Historical documentation and comparison files
- Multiple solution attempts and VPN troubleshooting guides

## old-scripts/
- Test scripts used during development
- Docker compose configurations for various attempts  
- Installation and diagnostic scripts
- Performance optimization attempts

## What Worked
The final working solutions are in the main directory:
1. **Mesa Version** - Universal compatibility
2. **NVIDIA OpenGL Version** - Hardware accelerated

Both use Microsoft's prebuilt packages instead of source compilation.
