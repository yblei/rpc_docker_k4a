"""Unit tests for the combined RpcDockerK4a class.

These tests mock Docker and system interactions to validate logic without
starting real containers or requiring NVIDIA toolkit.
"""

from unittest.mock import patch, MagicMock
import types
import subprocess
import pytest

from rpc_docker_k4a.combined import RpcDockerK4a


def test_init_no_auto_start_uses_available_port_and_sets_defaults():
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        assert k4a._host == 'localhost'
        assert 8000 <= k4a._port <= 8099
        assert k4a.server_container_id is None
        # xmlrpc ServerProxy creation shouldn't attempt a connection yet
        assert hasattr(k4a, 'server')
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
@patch.object(RpcDockerK4a, '_check_nvidia_container_toolkit', return_value=True)
def test_determine_strategy_nvidia_when_toolkit_available(mock_toolkit, mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        with patch.object(k4a, '_check_docker_image_exists', return_value=True):
            image_type, image_name = k4a._determine_docker_strategy()
        assert image_type == 'nvidia'
        assert image_name == 'azure-kinect-prebuilt-vpn'
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
@patch.object(RpcDockerK4a, '_check_nvidia_container_toolkit', return_value=False)
def test_determine_strategy_mesa_when_no_toolkit(mock_toolkit, mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        with patch.object(k4a, '_check_docker_image_exists', return_value=True):
            image_type, image_name = k4a._determine_docker_strategy()
        assert image_type == 'mesa'
        assert image_name == 'azure-kinect-mesa-vpn'
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
def test_determine_strategy_custom_image_builds_when_missing(mock_docker):
    # Custom image name controls the inferred type ('prebuilt' -> nvidia)
    k4a = RpcDockerK4a(auto_start=False, verbose=False, docker_image='my-prebuilt-vpn-custom')
    try:
        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=True), \
             patch.object(k4a, '_check_docker_image_exists', return_value=False) as mock_exists, \
             patch.object(k4a, '_build_docker_image', return_value='azure-kinect-prebuilt-vpn') as mock_build:
            image_type, image_name = k4a._determine_docker_strategy()

        assert image_type == 'nvidia'
        # When building, current implementation returns the default built image name
        assert image_name == 'azure-kinect-prebuilt-vpn'
        mock_exists.assert_called_with('my-prebuilt-vpn-custom')
        mock_build.assert_called_once_with('nvidia')
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
def test_determine_strategy_raises_when_image_missing_and_no_autobuild(mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False, use_docker='mesa', auto_build=False)
    try:
        with patch.object(k4a, '_check_docker_image_exists', return_value=False):
            with pytest.raises(RuntimeError):
                k4a._determine_docker_strategy()
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_check_docker_available', return_value=True)
def test_start_docker_server_sets_container_id_and_uses_expected_args(mock_docker):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        captured_cmd = {}

        def fake_run(cmd, capture_output=True, text=True, timeout=30):
            # Capture the command for assertions
            captured_cmd['cmd'] = cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout='container123\n', stderr='')

        with patch('subprocess.run', side_effect=fake_run):
            k4a._start_docker_server('mesa', 'azure-kinect-mesa-vpn')

        assert k4a.server_container_id == 'container123'
        cmd = captured_cmd['cmd']
        # Basic structure assertions
        assert cmd[:4] == ['docker', 'run', '--rm', '-d']
        assert '--network=host' in cmd
        assert 'azure-kinect-mesa-vpn' in cmd
        # Server entrypoint
        assert 'python3' in cmd
        assert '/workspace/rpc_docker_k4a/server.py' in cmd
    finally:
        k4a.close()


@patch.object(RpcDockerK4a, '_build_docker_image', return_value='built-image')
def test_build_image_auto_infers_type(mock_build):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=True):
            name = k4a.build_image('auto')
            assert name == 'built-image'
            mock_build.assert_called_with('nvidia')

        mock_build.reset_mock()
        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=False):
            name = k4a.build_image('auto')
            assert name == 'built-image'
            mock_build.assert_called_with('mesa')
    finally:
        k4a.close()


def test_get_server_info_reports_state():
    k4a = RpcDockerK4a(auto_start=False, verbose=False, use_docker='auto', docker_image='auto')
    try:
        # Pretend container is running
        k4a.server_container_id = 'abc123'
        with patch.object(k4a, '_check_nvidia_container_toolkit', return_value=False):
            info = k4a.get_server_info()
        assert info['host'] == k4a._host
        assert info['port'] == k4a._port
        assert info['docker_mode'] == 'auto'
        assert info['docker_image'] == 'auto'
        assert info['auto_build'] is True
        assert info['using_docker'] is True
        assert info['container_id'] == 'abc123'
    finally:
        k4a.close()


def test_restart_server_calls_cleanup_and_start(monkeypatch):
    k4a = RpcDockerK4a(auto_start=False, verbose=False)
    try:
        calls = []
        monkeypatch.setattr(k4a, '_cleanup', lambda: calls.append('cleanup'))
        monkeypatch.setattr(k4a, '_start_server', lambda: calls.append('start'))
        k4a.restart_server()
        assert calls == ['cleanup', 'start']
    finally:
        k4a.close()
