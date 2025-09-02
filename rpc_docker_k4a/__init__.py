"""
RPC Docker K4A - Azure Kinect Remote Procedure Call Docker Package

A comprehensive Python package for Azure Kinect sensor access through Docker containers
with XML-RPC server capabilities for remote depth sensing and image capture.

Main class for end users:
    RpcDockerK4a - Combined server/client class with automatic server management

Example usage:
    from rpc_docker_k4a import RpcDockerK4a
    
    # Automatically starts server and provides client interface
    with RpcDockerK4a() as k4a:
        k4a.connect_and_start()
        k4a.capture_and_save(count=10)
"""

__version__ = "1.0.0"
__author__ = "Azure Kinect RPC Team"
__email__ = "support@example.com"

# Primary class for end users
from .combined import RpcDockerK4a

# Advanced classes for custom implementations
from .server import AzureKinectRPCServer
from .client import AzureKinectRPCClient
from . import utils

# Main export - this is what users should primarily use
__all__ = ["RpcDockerK4a", "AzureKinectRPCServer", "AzureKinectRPCClient", "utils"]
