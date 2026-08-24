"""
Shared fixtures for WiFi-DensePose tests.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture()
def mock_sensing_state():
    return {
        "tick": 0,
        "source": "simulated",
        "total_detections": 0,
        "start_time": None,
    }


@pytest.fixture()
def sample_csi_frame():
    return {
        "node_id": 1,
        "n_antennas": 2,
        "n_subcarriers": 56,
        "freq_mhz": 2432,
        "sequence": 1,
        "rssi": -50,
        "noise_floor": -95,
        "amplitudes": [0.1] * 112,
        "phases": [0.0] * 112,
    }
