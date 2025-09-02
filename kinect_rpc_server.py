#!/usr/bin/env python3
"""
Azure Kinect RPC Server
Exposes Azure Kinect functionality over XML-RPC for remote access

Usage:
    python3 kinect_rpc_server.py [--host HOST] [--port PORT]

Default: localhost:8000
"""

import sys
import argparse
import threading
import time
import base64
import json
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import numpy as np
import cv2

try:
    import pyk4a
    from pyk4a import Config, PyK4A, ColorResolution, DepthMode, FPS
    PYKR4A_AVAILABLE = True
except ImportError:
    print("Warning: pyk4a not available. Server will run in simulation mode.")
    PYKR4A_AVAILABLE = False

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class AzureKinectRPCServer:
    def __init__(self):
        self.k4a = None
        self.is_started = False
        self.lock = threading.Lock()
        self.last_capture = None
        self.capture_thread = None
        self.auto_capture = False
        
    def device_connect(self, config_dict=None):
        """
        Connect to Azure Kinect device
        
        Args:
            config_dict (dict): Configuration parameters
                - color_resolution: str ('720P', '1080P', '1440P', '2160P')
                - depth_mode: str ('NFOV_UNBINNED', 'NFOV_2X2BINNED', 'WFOV_UNBINNED', 'WFOV_2X2BINNED')
                - camera_fps: int (5, 15, 30)
                - synchronized_images_only: bool
                
        Returns:
            dict: {'success': bool, 'message': str, 'serial': str}
        """
        try:
            with self.lock:
                if not PYKR4A_AVAILABLE:
                    return {
                        'success': False,
                        'message': 'pyk4a not available - running in simulation mode',
                        'serial': 'SIM000001'
                    }
                
                if self.k4a is not None:
                    return {'success': False, 'message': 'Device already connected'}
                
                # Default configuration
                if config_dict is None:
                    config_dict = {}
                
                # Parse configuration
                color_res = getattr(ColorResolution, f"RES_{config_dict.get('color_resolution', '720P')}")
                depth_mode = getattr(DepthMode, config_dict.get('depth_mode', 'NFOV_UNBINNED'))
                fps = getattr(FPS, f"FPS_{config_dict.get('camera_fps', 30)}")
                
                config = Config(
                    color_resolution=color_res,
                    depth_mode=depth_mode,
                    camera_fps=fps,
                    synchronized_images_only=config_dict.get('synchronized_images_only', True)
                )
                
                self.k4a = PyK4A(config)
                serial = "K4A_DEVICE_001"  # Placeholder - real implementation would get actual serial
                
                return {
                    'success': True,
                    'message': 'Device connected successfully',
                    'serial': serial
                }
                
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}
    
    def device_start(self):
        """
        Start the Azure Kinect device
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            with self.lock:
                if not PYKR4A_AVAILABLE:
                    self.is_started = True
                    return {'success': True, 'message': 'Device started (simulation mode)'}
                
                if self.k4a is None:
                    return {'success': False, 'message': 'Device not connected'}
                
                if self.is_started:
                    return {'success': False, 'message': 'Device already started'}
                
                self.k4a.start()
                self.is_started = True
                
                return {'success': True, 'message': 'Device started successfully'}
                
        except Exception as e:
            return {'success': False, 'message': f'Start failed: {str(e)}'}
    
    def device_stop(self):
        """
        Stop the Azure Kinect device
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            with self.lock:
                if not PYKR4A_AVAILABLE:
                    self.is_started = False
                    return {'success': True, 'message': 'Device stopped (simulation mode)'}
                
                if not self.is_started:
                    return {'success': False, 'message': 'Device not started'}
                
                self.auto_capture = False
                if self.capture_thread:
                    self.capture_thread.join(timeout=2.0)
                
                if self.k4a:
                    self.k4a.stop()
                    
                self.is_started = False
                return {'success': True, 'message': 'Device stopped successfully'}
                
        except Exception as e:
            return {'success': False, 'message': f'Stop failed: {str(e)}'}
    
    def device_disconnect(self):
        """
        Disconnect from Azure Kinect device
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            with self.lock:
                if self.is_started:
                    self.device_stop()
                
                self.k4a = None
                return {'success': True, 'message': 'Device disconnected'}
                
        except Exception as e:
            return {'success': False, 'message': f'Disconnect failed: {str(e)}'}
    
    def get_capture(self, timeout_ms=1000):
        """
        Get a single capture from the device
        
        Args:
            timeout_ms (int): Timeout in milliseconds
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'color_shape': list,
                'depth_shape': list,
                'ir_shape': list,
                'timestamp': float
            }
        """
        try:
            with self.lock:
                if not self.is_started:
                    return {'success': False, 'message': 'Device not started'}
                
                if not PYKR4A_AVAILABLE:
                    # Simulation mode
                    return {
                        'success': True,
                        'message': 'Capture successful (simulation)',
                        'color_shape': [720, 1280, 4],
                        'depth_shape': [576, 640],
                        'ir_shape': [576, 640],
                        'timestamp': time.time()
                    }
                
                capture = self.k4a.get_capture()
                self.last_capture = capture
                
                result = {
                    'success': True,
                    'message': 'Capture successful',
                    'timestamp': time.time()
                }
                
                if capture.color is not None:
                    result['color_shape'] = list(capture.color.shape)
                if capture.depth is not None:
                    result['depth_shape'] = list(capture.depth.shape)
                if capture.ir is not None:
                    result['ir_shape'] = list(capture.ir.shape)
                
                return result
                
        except Exception as e:
            return {'success': False, 'message': f'Capture failed: {str(e)}'}
    
    def get_color_image(self, format='BGR', quality=95):
        """
        Get color image from last capture
        
        Args:
            format (str): Image format ('BGR', 'RGB', 'JPEG', 'PNG')
            quality (int): JPEG quality (1-100)
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'image_data': str (base64 encoded),
                'shape': list,
                'format': str
            }
        """
        try:
            if self.last_capture is None or self.last_capture.color is None:
                return {'success': False, 'message': 'No color data available'}
            
            color = self.last_capture.color
            
            if not PYKR4A_AVAILABLE:
                # Create dummy image for simulation
                color = np.zeros((720, 1280, 4), dtype=np.uint8)
                color[:, :, :3] = [100, 150, 200]  # Blue-ish color
                color[:, :, 3] = 255  # Alpha
            
            # Convert based on requested format
            if format == 'BGR':
                image = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
                _, encoded = cv2.imencode('.png', image)
            elif format == 'RGB':
                image = cv2.cvtColor(color, cv2.COLOR_BGRA2RGB)
                _, encoded = cv2.imencode('.png', image)
            elif format == 'JPEG':
                image = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                _, encoded = cv2.imencode('.jpg', image, encode_param)
            elif format == 'PNG':
                image = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
                _, encoded = cv2.imencode('.png', image)
            else:
                return {'success': False, 'message': f'Unsupported format: {format}'}
            
            image_b64 = base64.b64encode(encoded.tobytes()).decode('utf-8')
            
            return {
                'success': True,
                'message': 'Color image retrieved',
                'image_data': image_b64,
                'shape': list(color.shape),
                'format': format
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Color image failed: {str(e)}'}
    
    def get_depth_image(self, format='RAW', min_depth=0, max_depth=4000):
        """
        Get depth image from last capture
        
        Args:
            format (str): 'RAW' (uint16), 'NORMALIZED' (uint8), 'COLORMAP' (uint8 BGR)
            min_depth (int): Minimum depth in mm
            max_depth (int): Maximum depth in mm
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'image_data': str (base64 encoded),
                'shape': list,
                'format': str,
                'depth_range': [min, max]
            }
        """
        try:
            if not PYKR4A_AVAILABLE:
                # Create dummy depth image
                depth = np.random.randint(500, 3000, (576, 640), dtype=np.uint16)
            else:
                if self.last_capture is None or self.last_capture.depth is None:
                    return {'success': False, 'message': 'No depth data available'}
                depth = self.last_capture.depth
            
            # Apply depth range filter
            depth_filtered = np.clip(depth, min_depth, max_depth)
            
            if format == 'RAW':
                # Return raw uint16 data
                encoded = depth_filtered.tobytes()
                image_b64 = base64.b64encode(encoded).decode('utf-8')
                result_shape = list(depth_filtered.shape) + ['uint16']
                
            elif format == 'NORMALIZED':
                # Normalize to 0-255
                depth_norm = cv2.normalize(depth_filtered, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                _, encoded = cv2.imencode('.png', depth_norm)
                image_b64 = base64.b64encode(encoded.tobytes()).decode('utf-8')
                result_shape = list(depth_norm.shape)
                
            elif format == 'COLORMAP':
                # Apply colormap for visualization
                depth_norm = cv2.normalize(depth_filtered, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                depth_colored = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
                _, encoded = cv2.imencode('.png', depth_colored)
                image_b64 = base64.b64encode(encoded.tobytes()).decode('utf-8')
                result_shape = list(depth_colored.shape)
                
            else:
                return {'success': False, 'message': f'Unsupported format: {format}'}
            
            return {
                'success': True,
                'message': 'Depth image retrieved',
                'image_data': image_b64,
                'shape': result_shape,
                'format': format,
                'depth_range': [int(depth_filtered.min()), int(depth_filtered.max())]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Depth image failed: {str(e)}'}
    
    def get_device_info(self):
        """
        Get device information
        
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'connected': bool,
                'started': bool,
                'serial': str,
                'available_modes': dict
            }
        """
        available_modes = {
            'color_resolutions': ['720P', '1080P', '1440P', '2160P'],
            'depth_modes': ['NFOV_UNBINNED', 'NFOV_2X2BINNED', 'WFOV_UNBINNED', 'WFOV_2X2BINNED'],
            'frame_rates': [5, 15, 30]
        }
        
        return {
            'success': True,
            'message': 'Device info retrieved',
            'connected': self.k4a is not None,
            'started': self.is_started,
            'serial': 'K4A_DEVICE_001' if self.k4a else None,
            'available_modes': available_modes,
            'simulation_mode': not PYKR4A_AVAILABLE
        }
    
    def start_auto_capture(self, interval_ms=33):
        """
        Start automatic capture in background thread
        
        Args:
            interval_ms (int): Capture interval in milliseconds (33ms = ~30fps)
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            if self.auto_capture:
                return {'success': False, 'message': 'Auto capture already running'}
            
            if not self.is_started:
                return {'success': False, 'message': 'Device not started'}
            
            self.auto_capture = True
            self.capture_thread = threading.Thread(
                target=self._auto_capture_loop,
                args=(interval_ms / 1000.0,),
                daemon=True
            )
            self.capture_thread.start()
            
            return {'success': True, 'message': 'Auto capture started'}
            
        except Exception as e:
            return {'success': False, 'message': f'Auto capture failed: {str(e)}'}
    
    def stop_auto_capture(self):
        """
        Stop automatic capture
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        self.auto_capture = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        return {'success': True, 'message': 'Auto capture stopped'}
    
    def _auto_capture_loop(self, interval):
        """Internal method for auto capture loop"""
        while self.auto_capture and self.is_started:
            try:
                self.get_capture()
                time.sleep(interval)
            except Exception as e:
                print(f"Auto capture error: {e}")
                break

def main():
    parser = argparse.ArgumentParser(description='Azure Kinect RPC Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create server
    server = SimpleXMLRPCServer((args.host, args.port), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()
    
    # Create and register Azure Kinect service
    kinect_service = AzureKinectRPCServer()
    server.register_instance(kinect_service)
    
    print(f"Azure Kinect RPC Server starting on {args.host}:{args.port}")
    if not PYKR4A_AVAILABLE:
        print("Warning: Running in simulation mode (pyk4a not available)")
    print("Available methods:")
    print("  - device_connect(config_dict)")
    print("  - device_start()")
    print("  - device_stop()")
    print("  - device_disconnect()")
    print("  - get_capture(timeout_ms)")
    print("  - get_color_image(format, quality)")
    print("  - get_depth_image(format, min_depth, max_depth)")
    print("  - get_device_info()")
    print("  - start_auto_capture(interval_ms)")
    print("  - stop_auto_capture()")
    print("\nPress Ctrl+C to stop server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        kinect_service.device_disconnect()
        server.shutdown()

if __name__ == "__main__":
    main()
