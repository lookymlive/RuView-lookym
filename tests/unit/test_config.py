"""Unit tests for core WiFi-DensePose configuration and signal math."""

from wifi_densepose import validate_config


class TestConfigValidation:
    def test_valid_config(self):
        cfg = {"source": "simulated", "tick_ms": 100}
        assert validate_config(cfg) is True

    def test_invalid_tick_ms(self):
        cfg = {"source": "simulated", "tick_ms": 0}
        assert validate_config(cfg) is False
