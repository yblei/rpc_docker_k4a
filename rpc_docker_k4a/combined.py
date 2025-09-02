#!/usr/bin/env python3
"""
RPC Docker K4A - Combined Server and Client Class

A unified interface that manages both the RPC server and client,
automatically starting the server in a Docker container when needed.
PyK4A is assumed to never be available on the host system.
"""

import os
import sys
import time
import socket
import subprocess
from typing import Optional, Union, Tuple, Any, Dict, List
import atexit

# Import the client class
from .client import AzureKinectRPCClient


class RpcDockerK4a(AzureKinectRPCClient):
    """
    Combined RPC Server and Client for Azure Kinect
    
    This class automatically manages the RPC server lifecycle, starting it
    in a Docker container when instantiated and cleaning it up when destroyed.
    It inherits all client functionality from AzureKinectRPCClient.
    
    PyK4A is assumed to never be available on the host system, so this
    class will automatically build and run the appropriate Docker container
    based on available hardware acceleration.
    
    Example:
        >>> # Basic usage with auto-detection and building
        >>> with RpcDockerK4a() as k4a:
        ...     devices = k4a.device_get_installed_count()
        ...     print(f"Found {devices} devices")
        
        >>> # Force NVIDIA Docker (will build if needed)
        >>> k4a = RpcDockerK4a(use_docker='nvidia', verbose=True)
        >>> try:
        ...     devices = k4a.device_get_installed_count()
        ... finally:
        ...     k4a.close()
        
        >>> # Force Mesa Docker (will build if needed)
        >>> k4a = RpcDockerK4a(use_docker='mesa', verbose=True)
        >>> devices = k4a.device_get_installed_count()
        >>> k4a.close()
    """
    
    def __init__(
        self,
        port: Optional[int] = None,
        host: str = 'localhost',
        timeout: float = 60.0,  # Increased for container building
        use_docker: str = 'auto',
        docker_image: str = 'auto',
        verbose: bool = False,
        auto_start: bool = True,
        auto_build: bool = True
    ):
        """
        Initialize the RPC Docker K4A combined client
        
        Args:
            port: Server port to use. If None, will find an available port
            host: Server host address
            timeout: Connection timeout in seconds (increased for building)
            use_docker: Docker usage strategy:
                - 'auto': Auto-detect best Docker setup and build if needed
                - 'nvidia': Force NVIDIA Docker container (build if needed)
                - 'mesa': Force Mesa Docker container (build if needed)
            docker_image: Docker image to use:
                - 'auto': Auto-detect and build best available image
                - Specific image name (e.g., 'azure-kinect-prebuilt-vpn')
            verbose: Enable verbose output
            auto_start: Automatically start server on initialization
            auto_build: Automatically build Docker images if they don't exist
        """
        self.use_docker = use_docker
        self.docker_image = docker_image
        self.verbose = verbose
        self.auto_build = auto_build
        self.server_container_id = None
        self._port = port
        self._host = host
        self._timeout = timeout
        self._cleanup_registered = False
        
        # Find available port if not specified
        if self._port is None:
            self._port = self._find_available_port(8000)
            
        if self.verbose:
            print(f"📡 Initializing RPC Docker K4A on {self._host}:{self._port}")
            print(f"   Docker mode: {self.use_docker}")
            print(f"   Docker image: {self.docker_image}")
            print(f"   Auto-build: {self.auto_build}")
        
        # Start server if requested
        if auto_start:
            self._start_server()
        
        # Initialize parent client class
        super().__init__(host=self._host, port=self._port)
        
        # Register cleanup
        if not self._cleanup_registered:
            atexit.register(self._cleanup)
            self._cleanup_registered = True
    
    def _find_available_port(self, start_port: int) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"Could not find available port starting from {start_port}")
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_nvidia_container_toolkit(self) -> bool:
        """Check if NVIDIA Container Toolkit is installed"""
        try:
            # Check for nvidia-container-runtime
            result = subprocess.run(['which', 'nvidia-container-runtime'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
            
            # Check Docker daemon configuration
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                info_output = result.stdout.lower()
                return 'nvidia' in info_output or 'container-runtime' in info_output
            
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_docker_image_exists(self, image_name: str) -> bool:
        """Check if Docker image exists locally"""
        try:
            result = subprocess.run(['docker', 'images', '-q', image_name], 
                                  capture_output=True, text=True, timeout=10)
            return bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _find_build_script(self, script_name: str) -> Optional[str]:
        """Find the Docker build script"""
        # First try to find in package installation (pip install case)
        try:
            # Get the package directory
            package_dir = os.path.dirname(__file__)
            docker_dir = os.path.join(package_dir, 'docker')
            
            if os.path.exists(docker_dir):
                script_path = os.path.join(docker_dir, script_name)
                if os.path.exists(script_path):
                    # Make sure it's executable
                    import stat
                    current_mode = os.stat(script_path).st_mode
                    os.chmod(script_path, current_mode | stat.S_IEXEC)
                    return script_path
        except Exception as e:
            if self.verbose:
                print(f"   Package location search failed: {e}")
        
        # Fallback: Look in development/source locations
        possible_paths = [
            os.path.join(os.getcwd(), 'rpc_docker_k4a', 'docker', script_name),
            os.path.join(os.getcwd(), 'docker', script_name),
            os.path.join(os.getcwd(), script_name),
            script_name
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # If not executable, try to make it executable
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    import stat
                    current_mode = os.stat(path).st_mode
                    os.chmod(path, current_mode | stat.S_IEXEC)
                    if os.access(path, os.X_OK):
                        return path
                except:
                    continue
        
        return None
    
    def _build_docker_image(self, image_type: str) -> str:
        """Build the Docker image and return the image name"""
        if image_type == 'nvidia':
            script_name = 'build-prebuilt-vpn.sh'
            dockerfile_name = 'Dockerfile.k4a-prebuilt'
            image_name = 'azure-kinect-prebuilt-vpn'
        elif image_type == 'mesa':
            script_name = 'build-mesa-vpn.sh'
            dockerfile_name = 'Dockerfile.mesa'
            image_name = 'azure-kinect-mesa-vpn'
        else:
            raise ValueError(f"Unknown image type: {image_type}")
        
        if self.verbose:
            print(f"🔨 Building {image_type} Docker image: {image_name}")
        
        # Find the build script
        script_path = self._find_build_script(script_name)
        if script_path is None:
            raise RuntimeError(f"Build script '{script_name}' not found")
        
        # Get the docker directory (where Dockerfile and other files are)
        docker_dir = os.path.dirname(script_path)
        
        if self.verbose:
            print(f"   Using script: {script_path}")
            print(f"   Docker directory: {docker_dir}")
        
        # Verify required files exist
        dockerfile_path = os.path.join(docker_dir, dockerfile_name)
        rules_file_path = os.path.join(docker_dir, '99-k4a.rules')
        
        if not os.path.exists(dockerfile_path):
            raise RuntimeError(f"Dockerfile not found: {dockerfile_path}")
        
        if not os.path.exists(rules_file_path):
            # Try to copy from package directory
            package_rules = os.path.join(os.path.dirname(__file__), '99-k4a.rules')
            if os.path.exists(package_rules):
                import shutil
                shutil.copy2(package_rules, rules_file_path)
                if self.verbose:
                    print(f"   Copied 99-k4a.rules to docker directory")
            else:
                if self.verbose:
                    print(f"   Warning: 99-k4a.rules not found, build may fail")
        
        # Run the build script
        try:
            result = subprocess.run(
                [script_path], 
                capture_output=not self.verbose, 
                text=True, 
                timeout=1800,  # 30 minutes for building
                cwd=docker_dir
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Build failed"
                raise RuntimeError(f"Failed to build {image_type} image: {error_msg}")
            
            if self.verbose:
                print(f"✅ Successfully built {image_name}")
            
            return image_name
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Docker image build timed out after 30 minutes")
        except FileNotFoundError:
            raise RuntimeError(f"Build script not executable: {script_path}")
        except PermissionError:
            raise RuntimeError(f"Permission denied executing build script: {script_path}")
    
    def _determine_docker_strategy(self) -> Tuple[str, str]:
        """
        Determine the best Docker strategy and ensure image is available
        
        Returns:
            (image_type: str, image_name: str)
        """
        if not self._check_docker_available():
            raise RuntimeError("Docker is not available. This tool requires Docker to run PyK4A.")
        
        # Determine which image type to use
        if self.use_docker == 'nvidia':
            image_type = 'nvidia'
            image_name = 'azure-kinect-prebuilt-vpn'
        elif self.use_docker == 'mesa':
            image_type = 'mesa'
            image_name = 'azure-kinect-mesa-vpn'
        else:  # auto or specific image
            if self.docker_image != 'auto':
                # User specified a specific image name
                image_name = self.docker_image
                image_type = 'nvidia' if 'prebuilt' in image_name else 'mesa'
            else:
                # Auto-detect best image type
                if self._check_nvidia_container_toolkit():
                    if self.verbose:
                        print("✅ NVIDIA Container Toolkit detected - using NVIDIA acceleration")
                    image_type = 'nvidia'
                    image_name = 'azure-kinect-prebuilt-vpn'
                else:
                    if self.verbose:
                        print("⚠️  NVIDIA Container Toolkit not found - using Mesa software rendering")
                    image_type = 'mesa'
                    image_name = 'azure-kinect-mesa-vpn'
        
        # Check if image exists, build if needed
        if not self._check_docker_image_exists(image_name):
            if self.auto_build:
                if self.verbose:
                    print(f"📦 Image '{image_name}' not found, building automatically...")
                image_name = self._build_docker_image(image_type)
            else:
                raise RuntimeError(
                    f"Docker image '{image_name}' not found and auto_build is disabled. "
                    f"Build it manually with: ./rpc_docker_k4a/docker/build-{'prebuilt-vpn' if image_type == 'nvidia' else 'mesa-vpn'}.sh"
                )
        elif self.verbose:
            print(f"✅ Found existing image: {image_name}")
        
        return image_type, image_name
    
    def _start_server(self):
        """Start the RPC server in a Docker container"""
        if self.server_container_id is not None:
            if self.verbose:
                print("⚠️  Server already running")
            return
        
        image_type, image_name = self._determine_docker_strategy()
        self._start_docker_server(image_type, image_name)
        
        # Wait for server to start
        if self.verbose:
            print(f"⏳ Waiting for server to start on {self._host}:{self._port}")
        
        for attempt in range(int(self._timeout)):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    result = s.connect_ex((self._host, self._port))
                    if result == 0:
                        if self.verbose:
                            print(f"✅ Server started successfully!")
                        return
            except:
                pass
            time.sleep(1)
        
        raise RuntimeError(f"Server failed to start within {self._timeout} seconds")
    
    def _start_docker_server(self, image_type: str, image_name: str):
        """Start server in Docker container"""
        if self.verbose:
            print(f"🐳 Starting Docker server with {image_type} image: {image_name}")
        
        # Build command based on image type
        cmd = ['docker', 'run', '--rm', '-d']
        
        # Add runtime for NVIDIA
        if image_type == 'nvidia' and self._check_nvidia_container_toolkit():
            cmd.extend(['--runtime=nvidia'])
            if self.verbose:
                print("   Using NVIDIA runtime")
        
        # Add necessary Docker arguments for Kinect access
        cmd.extend([
            '--privileged',
            '--network=host',  # Use host networking for simplicity
            '-e', 'DISPLAY=:0',
            '-v', '/tmp/.X11-unix:/tmp/.X11-unix:rw',
            '-v', '/dev:/dev:rw',
            '-v', '/etc/udev/rules.d:/etc/udev/rules.d:rw',
            '--device-cgroup-rule=c 81:* rmw',
            '--device-cgroup-rule=c 189:* rmw'
        ])
        
        # Mount current directory to access RPC server
        current_dir = os.path.abspath(os.path.dirname(__file__))
        workspace_root = os.path.dirname(current_dir)  # Go up from rpc_docker_k4a to workspace root
        cmd.extend(['-v', f'{workspace_root}:/workspace:rw'])
        
        # Add image and command - look for server in mounted workspace
        cmd.extend([
            image_name,
            'python3', '/workspace/rpc_docker_k4a/server.py',
            '--host', '0.0.0.0',
            '--port', str(self._port)
        ])
        
        if self.verbose:
            print(f"   Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to start Docker container: {result.stderr}")
            
            self.server_container_id = result.stdout.strip()
            if self.verbose:
                print(f"   Container ID: {self.server_container_id[:12]}")
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Docker container startup timed out")
        except FileNotFoundError:
            raise RuntimeError("Docker not found in PATH")
    
    def _cleanup(self):
        """Clean up server container"""
        if self.verbose and self.server_container_id:
            print("🧹 Cleaning up server...")
        
        # Stop Docker container
        if self.server_container_id:
            try:
                subprocess.run(['docker', 'stop', self.server_container_id], 
                             capture_output=True, timeout=10)
                if self.verbose:
                    print(f"   Stopped container: {self.server_container_id[:12]}")
            except subprocess.TimeoutExpired:
                if self.verbose:
                    print(f"   Force killing container: {self.server_container_id[:12]}")
                subprocess.run(['docker', 'kill', self.server_container_id], 
                             capture_output=True)
            except Exception as e:
                if self.verbose:
                    print(f"   Error stopping container: {e}")
            finally:
                self.server_container_id = None
    
    def close(self):
        """Close the connection and clean up the server"""
        if hasattr(super(), 'close'):
            super().close()
        self._cleanup()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        try:
            self._cleanup()
        except Exception:
            pass  # Ignore errors during cleanup in destructor
    
    def restart_server(self):
        """Restart the server"""
        if self.verbose:
            print("🔄 Restarting server...")
        self._cleanup()
        time.sleep(2)  # Give time for cleanup
        self._start_server()
        
        # Reconnect client
        if hasattr(self, '_proxy'):
            self._connect()
    
    def build_image(self, image_type: str = 'auto') -> str:
        """
        Manually build a Docker image
        
        Args:
            image_type: 'auto', 'nvidia', or 'mesa'
            
        Returns:
            Built image name
        """
        if image_type == 'auto':
            if self._check_nvidia_container_toolkit():
                image_type = 'nvidia'
            else:
                image_type = 'mesa'
        
        return self._build_docker_image(image_type)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the running server"""
        info = {
            'host': self._host,
            'port': self._port,
            'docker_mode': self.use_docker,
            'docker_image': self.docker_image,
            'auto_build': self.auto_build,
            'nvidia_toolkit_available': self._check_nvidia_container_toolkit(),
            'using_docker': self.server_container_id is not None,
        }
        
        if self.server_container_id:
            info['container_id'] = self.server_container_id
        
        return info


def main():
    """CLI entry point for the combined RPC client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Azure Kinect RPC Combined Client')
    parser.add_argument('--port', type=int, default=None, help='Server port (auto-detect if not specified)')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--timeout', type=float, default=60.0, help='Connection timeout')
    parser.add_argument('--docker', choices=['auto', 'nvidia', 'mesa'], 
                       default='auto', help='Docker image type')
    parser.add_argument('--image', default='auto', help='Docker image name')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--no-auto-start', action='store_true', help='Don\'t auto-start server')
    parser.add_argument('--no-auto-build', action='store_true', help='Don\'t auto-build images')
    parser.add_argument('--build-only', action='store_true', help='Only build image, don\'t start server')
    
    args = parser.parse_args()
    
    if args.build_only:
        # Only build the image
        try:
            k4a = RpcDockerK4a(
                use_docker=args.docker,
                docker_image=args.image,
                verbose=args.verbose,
                auto_start=False,
                auto_build=not args.no_auto_build
            )
            
            image_name = k4a.build_image(args.docker)
            print(f"✅ Successfully built image: {image_name}")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)
        return
    
    try:
        with RpcDockerK4a(
            port=args.port,
            host=args.host,
            timeout=args.timeout,
            use_docker=args.docker,
            docker_image=args.image,
            verbose=args.verbose,
            auto_start=not args.no_auto_start,
            auto_build=not args.no_auto_build
        ) as k4a:
            print("🎯 RPC Docker K4A Client Connected!")
            
            # Show server info
            info = k4a.get_server_info()
            print(f"\n📋 Server Information:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            # Test basic functionality
            print(f"\n🔍 Testing device detection...")
            try:
                device_count = k4a.device_get_installed_count()
                print(f"   Found {device_count} Azure Kinect device(s)")
                
                if device_count > 0:
                    print(f"\n📷 Getting device 0 serial number...")
                    serial = k4a.device_get_serialnum(0)
                    print(f"   Serial: {serial}")
                    
            except Exception as e:
                print(f"   Error: {e}")
            
            print(f"\n✅ Test completed successfully!")
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
