from unittest import mock

import pytest as pytest

URL = "/api/storage/v1/healthcheck"


def test_healthcheck_passes(client, storage_service_mock):
    storage_service_mock.ping.return_value = None

    resp = client.get(URL)

    assert resp.status_code == 200


def test_healthcheck_fails(client, storage_service_mock):
    storage_service_mock.ping.side_effect = Exception

    resp = client.get(URL)
    assert resp.status_code == 503
    assert resp.json()["detail"].startswith("FILE_STORAGE isn't configured properly:")

    resp = client.get(URL, params={"storage_type": "GCP_STORAGE"})
    assert resp.status_code == 503
    assert resp.json()["detail"].startswith("GCP_STORAGE isn't configured properly:")
