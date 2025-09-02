"""
Utility functions for the Azure Kinect RPC package
"""

import base64
import numpy as np
import cv2
from typing import Dict, Any, Optional, Tuple


def decode_image_from_rpc(image_data_b64: str, image_format: str = 'BGR') -> Optional[np.ndarray]:
    """
    Decode base64 image data from RPC response
    
    Args:
        image_data_b64: Base64 encoded image data
        image_format: Expected image format
        
    Returns:
        Decoded image as numpy array or None if failed
    """
    try:
        image_data = base64.b64decode(image_data_b64)
        if image_format in ['BGR', 'RGB', 'JPEG', 'PNG', 'COLORMAP', 'NORMALIZED']:
            image_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            return image_np
        elif image_format == 'RAW':
            # Raw uint16 depth data
            image_np = np.frombuffer(image_data, dtype=np.uint16)
            return image_np
        else:
            raise ValueError(f"Unsupported image format: {image_format}")
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def validate_k4a_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate Azure Kinect configuration parameters
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_color_resolutions = ['720P', '1080P', '1440P', '2160P']
    valid_depth_modes = ['NFOV_UNBINNED', 'NFOV_2X2BINNED', 'WFOV_UNBINNED', 'WFOV_2X2BINNED']
    valid_fps = [5, 15, 30]
    
    if 'color_resolution' in config:
        if config['color_resolution'] not in valid_color_resolutions:
            return False, f"Invalid color_resolution. Must be one of: {valid_color_resolutions}"
    
    if 'depth_mode' in config:
        if config['depth_mode'] not in valid_depth_modes:
            return False, f"Invalid depth_mode. Must be one of: {valid_depth_modes}"
    
    if 'camera_fps' in config:
        if config['camera_fps'] not in valid_fps:
            return False, f"Invalid camera_fps. Must be one of: {valid_fps}"
    
    if 'synchronized_images_only' in config:
        if not isinstance(config['synchronized_images_only'], bool):
            return False, "synchronized_images_only must be a boolean"
    
    return True, "Configuration is valid"


def create_default_config() -> Dict[str, Any]:
    """
    Create default Azure Kinect configuration
    
    Returns:
        Default configuration dictionary
    """
    return {
        'color_resolution': '720P',
        'depth_mode': 'NFOV_UNBINNED',
        'camera_fps': 30,
        'synchronized_images_only': True
    }


def save_image_data(image_data_b64: str, filename: str, image_format: str = 'PNG') -> bool:
    """
    Save base64 encoded image data to file
    
    Args:
        image_data_b64: Base64 encoded image data
        filename: Output filename
        image_format: Image format
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if image_format == 'RAW':
            # Save raw binary data
            image_data = base64.b64decode(image_data_b64)
            with open(filename, 'wb') as f:
                f.write(image_data)
        else:
            # Save decoded image
            image_np = decode_image_from_rpc(image_data_b64, image_format)
            if image_np is not None:
                cv2.imwrite(filename, image_np)
            else:
                return False
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def format_device_info(info: Dict[str, Any]) -> str:
    """
    Format device info dictionary for display
    
    Args:
        info: Device info dictionary
        
    Returns:
        Formatted string
    """
    output = []
    output.append("=== Device Information ===")
    output.append(f"Connected: {info.get('connected', 'Unknown')}")
    output.append(f"Started: {info.get('started', 'Unknown')}")
    output.append(f"Serial: {info.get('serial', 'N/A')}")
    output.append(f"Simulation Mode: {info.get('simulation_mode', False)}")
    
    if 'available_modes' in info:
        modes = info['available_modes']
        output.append(f"Available color resolutions: {', '.join(modes.get('color_resolutions', []))}")
        output.append(f"Available depth modes: {', '.join(modes.get('depth_modes', []))}")
        output.append(f"Available frame rates: {', '.join(map(str, modes.get('frame_rates', [])))}")
    
    return '\n'.join(output)


def check_rpc_response(response: Dict[str, Any], operation: str = "operation") -> bool:
    """
    Check if RPC response indicates success
    
    Args:
        response: RPC response dictionary
        operation: Name of the operation for error messages
        
    Returns:
        True if successful, False otherwise
    """
    if not isinstance(response, dict):
        print(f"{operation} failed: Invalid response format")
        return False
    
    if not response.get('success', False):
        message = response.get('message', 'Unknown error')
        print(f"{operation} failed: {message}")
        return False
    
    return True


def estimate_image_size(shape: list, format: str = 'BGR') -> int:
    """
    Estimate image size in bytes based on shape and format
    
    Args:
        shape: Image shape [height, width, channels]
        format: Image format
        
    Returns:
        Estimated size in bytes
    """
    if len(shape) < 2:
        return 0
    
    height, width = shape[:2]
    channels = shape[2] if len(shape) > 2 else 1
    
    if format == 'RAW':
        # Assume 16-bit depth data
        return height * width * 2
    elif format in ['JPEG']:
        # Rough JPEG compression estimate
        return (height * width * channels) // 10
    else:
        # Uncompressed or PNG
        return height * width * channels
