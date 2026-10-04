import pytest
import io
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

from client.services.config_manager import ClientConfigManager
from client.services.network_client import NetworkClient

def test_config_manager_load_and_save(tmp_path):
    cfg_file = tmp_path / "test_settings.json"
    mgr = ClientConfigManager(config_path=cfg_file)

    # Initial load returns defaults
    data = mgr.load()
    assert data["server_host"] == "127.0.0.1"
    assert data["server_port"] == 8000

    # Save modified
    data["server_host"] = "192.168.1.50"
    data["server_port"] = 9000
    mgr.save(data)

    # Re-load
    reloaded = mgr.load()
    assert reloaded["server_host"] == "192.168.1.50"
    assert reloaded["server_port"] == 9000

def test_client_sha256_computation(tmp_path):
    test_file = tmp_path / "sample_video.bin"
    content = b"Sample video test binary data for integrity check."
    test_file.write_bytes(content)

    net = NetworkClient()
    progress_updates = []
    
    def on_progress(p):
        progress_updates.append(p)

    calculated_hash = net.compute_sha256(test_file, progress_callback=on_progress)
    expected_hash = hashlib.sha256(content).hexdigest()

    assert calculated_hash == expected_hash
    assert len(progress_updates) > 0
    assert progress_updates[-1] == 1.0

def test_network_client_headers():
    client_no_token = NetworkClient(host="127.0.0.1", port=8000, api_token="")
    assert client_no_token.get_headers() == {}

    client_with_token = NetworkClient(host="127.0.0.1", port=8000, api_token="secret-123")
    assert client_with_token.get_headers() == {"X-API-Token": "secret-123"}
