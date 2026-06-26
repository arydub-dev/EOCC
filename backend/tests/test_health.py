"""Smoke tests for the application's system probes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_live_probe():
    with TestClient(app) as client:
        response = client.get("/live")
        assert response.status_code == 200


def test_health_reports_version():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert "version" in body
