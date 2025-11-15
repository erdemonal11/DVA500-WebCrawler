from unittest.mock import MagicMock, patch

from webcrawler.client import check_visited


def _mock_socket_with_response(resp: str):
    mock_sock = MagicMock()
    mock_conn = MagicMock()
    mock_sock.__enter__.return_value = mock_conn
    mock_conn.recv.return_value = resp.encode()
    return mock_sock


def test_check_visited_yes():
    with patch("socket.socket", return_value=_mock_socket_with_response("Y")):
        assert check_visited("http://example.com", host="h", port=1, process_id="1") is True


def test_check_visited_no():
    with patch("socket.socket", return_value=_mock_socket_with_response("N")):
        assert check_visited("http://example.com", host="h", port=1, process_id="1") is False
