from http import HTTPStatus

import pytest

URL = "/api/storage/v1/debug/500"


def test_debug_returns_500(client):
    with pytest.raises(ValueError):
        client.get(URL)
