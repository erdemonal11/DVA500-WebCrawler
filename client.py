import os
import sys
import time
import socket
import requests
import configparser
from bs4 import BeautifulSoup

process_id = sys.argv[1]  

pid = os.getpid()

url_to_visit = sys.argv[2]

config = configparser.ConfigParser()
config.read('crawler.cfg')
HOST = config['server']['host']  
PORT = int(config['server']['port'])

def request_with_retry(url, retries=5, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
        except requests.ConnectionError:
            print(f"[Process #{process_id}] Attempt {attempt + 1} failed to connect to {url}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"[Process #{process_id}] Failed to connect to {url} after {retries} attempts")

def check_visited(url):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(url.encode())
            response = s.recv(1024).decode()
            return response == 'Y'
    except Exception as e:
        print(f"[Process #{process_id}] Error connecting to the server: {e}")
        print(f"[Process #{process_id}] Exiting because server is unavailable.")
        sys.exit(1)

def visit(url):
    if check_visited(url):
        print(f"[Process #{process_id}] Skipping {url}, already visited.")
        return
    
    print(f"[Process #{process_id}] parsing {url}")
    reqs = request_with_retry(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    return

visit(url_to_visit)

print(f"[Process #{process_id}] completed, bye!")
time.sleep(1)
