from unittest.mock import MagicMock, patch

import requests

from webcrawler.client import request_with_retry


def test_request_with_retry_eventually_succeeds():
    url = "http://example.com"

    success_response = MagicMock()
    success_response.status_code = 200

    call_sequence = [requests.ConnectionError(), requests.ConnectionError(), success_response]

    def fake_get(_):
        result = call_sequence.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    with patch("requests.get", side_effect=fake_get):
        resp = request_with_retry(url, retries=3, delay=0, process_id="1")
        assert resp.status_code == 200
