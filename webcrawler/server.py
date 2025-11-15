import configparser
import logging
import os
import socket
import time
from datetime import datetime


def main():
    logger = logging.getLogger(__name__)
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

    visited = set()

    first_request_received = False
    start = datetime.now()
    end = datetime.now()

    config = configparser.ConfigParser()
    config.read("crawler.cfg")
    PORT = int(config["server"]["port"])

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", PORT))
    soc.listen()
    logger.info("Listening on port %s... Press CTRL+C to quit", PORT)

    try:
        while True:
            conn, addr = soc.accept()
            url = conn.recv(1024).decode()
            if not url:
                logger.warning("Received empty URL from %s", addr)
                conn.close()
                continue
            res = "Y" if url in visited else "N"
            logger.debug("Visited check for %s -> %s", url, res)
            visited.add(url)
            conn.sendall(res.encode())
            conn.close()
            if not first_request_received:
                first_request_received = True
                start = datetime.now()
            end = datetime.now()

    except KeyboardInterrupt:
        soc.close()
        logger.info(
            "Socket on port %s closed. %d pages found in %s seconds. Exiting in 5 seconds...",
            PORT,
            len(visited),
            (end - start).total_seconds(),
        )
        time.sleep(5)
    except Exception as e:
        soc.close()
        logger.error("Unhandled server error: %s", e)


if __name__ == "__main__":
    main()
