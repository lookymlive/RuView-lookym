"""Integration tests for Rust sensing-server health endpoints."""

import subprocess
import time

import httpx


def _wait_for_server(base_url: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with httpx.Client(timeout=1.0) as client:
                r = client.get(f"{base_url}/health/live")
                if r.status_code == 200:
                    return
        except Exception:
            pass
        time.sleep(0.3)
    raise RuntimeError(f"Server did not become ready at {base_url}")


def test_health_endpoints():
    base = "http://127.0.0.1:3000"
    _wait_for_server(base, timeout=20.0)
    with httpx.Client(timeout=5.0) as client:
        live = client.get(f"{base}/health/live")
        assert live.status_code == 200
        assert live.json()["status"] == "alive"

        ready = client.get(f"{base}/health/ready")
        assert ready.status_code == 200
        assert ready.json()["status"] == "ready"

        info = client.get(f"{base}/api/v1/info")
        assert info.status_code == 200
        body = info.json()
        assert "version" in body
        assert "backend" in body
