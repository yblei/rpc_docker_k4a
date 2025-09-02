#!/usr/bin/env python3
"""
Test pip installation file structure
"""
import os
import sys

def test_pip_installation():
    """Test that all necessary files are available after pip install"""
    print("🧪 TESTING PIP INSTALLATION STRUCTURE")
    
    try:
        # Import the package
        import rpc_docker_k4a
        from rpc_docker_k4a.combined import RpcDockerK4a
        
        print(f"✅ Package imported from: {rpc_docker_k4a.__file__}")
        
        # Check package directory
        package_dir = os.path.dirname(rpc_docker_k4a.__file__)
        print(f"📁 Package directory: {package_dir}")
        
        # Check for docker directory
        docker_dir = os.path.join(package_dir, 'docker')
        if os.path.exists(docker_dir):
            print(f"✅ Docker directory found: {docker_dir}")
            
            # List docker files
            docker_files = os.listdir(docker_dir)
            print(f"📋 Docker files: {sorted(docker_files)}")
            
            # Check for required files
            required_files = [
                'build-prebuilt-vpn.sh',
                'build-mesa-vpn.sh', 
                'Dockerfile.k4a-prebuilt',
                'Dockerfile.mesa',
                '99-k4a.rules'
            ]
            
            for file in required_files:
                file_path = os.path.join(docker_dir, file)
                if os.path.exists(file_path):
                    executable = os.access(file_path, os.X_OK) if file.endswith('.sh') else 'N/A'
                    print(f"✅ {file} - exists: True, executable: {executable}")
                else:
                    print(f"❌ {file} - exists: False")
        else:
            print(f"❌ Docker directory not found: {docker_dir}")
        
        # Test combined class initialization
        k4a = RpcDockerK4a(auto_start=False, verbose=True)
        print(f"✅ RpcDockerK4a initialized successfully")
        
        # Test build script finding
        nvidia_script = k4a._find_build_script('build-prebuilt-vpn.sh')
        mesa_script = k4a._find_build_script('build-mesa-vpn.sh')
        
        print(f"🔍 NVIDIA script: {nvidia_script or 'NOT FOUND'}")
        print(f"🔍 Mesa script: {mesa_script or 'NOT FOUND'}")
        
        if nvidia_script and mesa_script:
            print(f"✅ ALL TESTS PASSED - Pip installation is properly configured")
        else:
            print(f"❌ TESTS FAILED - Missing build scripts after pip install")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pip_installation()
