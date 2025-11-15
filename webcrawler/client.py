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
    if check_visited(url, host, port, process_id):
        logger.info("[Process #%s] Skipping %s, already visited.", process_id, url)
        return

    logger.info("[Process #%s] parsing %s", process_id, url)
    reqs = request_with_retry(url, process_id=process_id)
    BeautifulSoup(reqs.text, "html.parser")
    return


def main():
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
