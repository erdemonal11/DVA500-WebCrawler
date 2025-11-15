import configparser
import logging
import os
import socket
import sys
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def request_with_retry(url, retries=5, delay=5, process_id=None):
    """
    Request a URL with retry mechanism.

    Attempts to fetch a URL with automatic retry on connection errors.
    Logs warnings for each failed attempt and raises an exception if all retries fail.

    Args:
        url (str): The URL to request.
        retries (int): Number of retry attempts. Defaults to 5.
        delay (int): Delay between retries in seconds. Defaults to 5.
        process_id (str, optional): Process identifier for logging purposes.

    Returns:
        requests.Response: Response object if the request succeeds.

    Raises:
        Exception: If all retry attempts fail to connect to the URL.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
        except requests.ConnectionError:
            logger.warning(
                "[Process #%s] Attempt %d failed to connect to %s. Retrying in %d seconds...",
                process_id,
                attempt + 1,
                url,
                delay,
            )
            time.sleep(delay)
    raise Exception(f"[Process #{process_id}] Failed to connect to {url} after {retries} attempts")


def check_visited(url, host, port, process_id):
    """
    Check if a URL has already been visited by querying the server.

    Connects to the server via socket and sends the URL. The server responds
    with 'Y' if the URL was visited, 'N' otherwise.

    Args:
        url (str): The URL to check.
        host (str): Server hostname or IP address.
        port (int): Server port number.
        process_id (str): Process identifier for logging purposes.

    Returns:
        bool: True if the URL was already visited, False otherwise.

    Raises:
        SystemExit: If connection to the server fails.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(url.encode())
            response = s.recv(1024).decode()
            logger.debug(
                "[Process #%s] URL: '%s' | Server Response: '%s'",
                process_id,
                url,
                response,
            )
            return response == "Y"
    except Exception as e:
        logger.error("[Process #%s] Error connecting to the server: %s", process_id, e)
        logger.error("[Process #%s] Exiting because server is unavailable.", process_id)
        sys.exit(1)


def visit(url, host, port, process_id):
    """
    Visit a URL if it hasn't been visited before.

    Checks with the server if the URL was already visited. If not, fetches
    the URL content and parses it with BeautifulSoup.

    Args:
        url (str): The URL to visit.
        host (str): Server hostname or IP address.
        port (int): Server port number.
        process_id (str): Process identifier for logging purposes.

    Returns:
        None: This function returns nothing.
    """
    if check_visited(url, host, port, process_id):
        logger.info("[Process #%s] Skipping %s, already visited.", process_id, url)
        return

    logger.info("[Process #%s] parsing %s", process_id, url)
    reqs = request_with_retry(url, process_id=process_id)
    BeautifulSoup(reqs.text, "html.parser")
    return


def main():
    """
    Main entry point for the web crawler client.

    Sets up logging, reads configuration, and visits the specified URL.
    Logs all operations and exits after completion.

    Command-line arguments:
        sys.argv[1]: Process ID for identification.
        sys.argv[2]: URL to visit.

    Environment variables:
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
    """
    process_id = sys.argv[1]
    url_to_visit = sys.argv[2]

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_name, logging.INFO)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        fh = logging.FileHandler("app.log")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)

    config = configparser.ConfigParser()
    config.read("crawler.cfg")
    HOST = config["server"]["host"]
    PORT = int(config["server"]["port"])

    visit(url_to_visit, HOST, PORT, process_id)

    logger.info("[Process #%s] completed, bye!", process_id)
    time.sleep(1)


if __name__ == "__main__":
    main()
