"""Minimal tests for RpcDockerK4a NVIDIA container behavior."""

from unittest.mock import patch
import subprocess

from rpc_docker_k4a.combined import RpcDockerK4a


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
def test_strategy_prefers_nvidia_when_toolkit_available(mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=True), \
             patch.object(k4a, '_check_docker_image_exists', return_value=True):
            image_type, image_name = k4a._determine_docker_strategy()

        assert image_type == 'nvidia'
        assert image_name == 'azure-kinect-prebuilt-vpn'
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
def test_start_uses_nvidia_runtime_flag_when_toolkit_available(mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        captured = {}

        def fake_run(cmd, capture_output=True, text=True, timeout=30):
            captured['cmd'] = cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='cid123\n', stderr='')

        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=True), \
             patch('subprocess.run', side_effect=fake_run):
            k4a._start_docker_server('nvidia', 'azure-kinect-prebuilt-vpn')

        cmd = captured['cmd']
        assert '--runtime=nvidia' in cmd
        assert 'azure-kinect-prebuilt-vpn' in cmd
        assert k4a.server_container_id == 'cid123'
    finally:
        k4a.close()
