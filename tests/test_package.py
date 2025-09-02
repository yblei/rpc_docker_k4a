"""Basic tests for the package structure"""

import pytest
import importlib


def test_package_import():
    """Test that the main package can be imported"""
    import rpc_docker_k4a
    assert rpc_docker_k4a.__version__ == "1.0.0"


def test_server_import():
    """Test that the server class can be imported"""
    from rpc_docker_k4a import AzureKinectRPCServer
    assert AzureKinectRPCServer is not None


def test_client_import():
    """Test that the client class can be imported"""
    from rpc_docker_k4a import AzureKinectRPCClient
    assert AzureKinectRPCClient is not None


def test_utils_import():
    """Test that utils module can be imported"""
    from rpc_docker_k4a import utils
    assert utils is not None


def test_utils_functions():
    """Test that utility functions exist"""
    from rpc_docker_k4a.utils import (
        decode_image_from_rpc,
        validate_k4a_config,
        create_default_config,
        format_device_info
    )
    
    # Test default config
    config = create_default_config()
    assert isinstance(config, dict)
    assert 'color_resolution' in config
    assert 'depth_mode' in config
    
    # Test config validation
    valid, message = validate_k4a_config(config)
    assert valid == True
    assert message == "Configuration is valid"


@pytest.mark.hardware
def test_server_initialization():
    """Test that server can be initialized (requires hardware)"""
    from rpc_docker_k4a import AzureKinectRPCServer
    
    server = AzureKinectRPCServer()
    assert server.k4a is None
    assert server.is_started == False


def test_client_initialization():
    """Test that client can be initialized"""
    from rpc_docker_k4a import AzureKinectRPCClient
    
    client = AzureKinectRPCClient('localhost', 8000)
    assert 'localhost' in client.server_url
    assert '8000' in client.server_url


def test_package_all():
    """Test that __all__ includes expected exports"""
    import rpc_docker_k4a
    
    expected = ["AzureKinectRPCServer", "AzureKinectRPCClient", "utils"]
    for item in expected:
        assert item in rpc_docker_k4a.__all__
        assert hasattr(rpc_docker_k4a, item)
