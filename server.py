import socket
import time
import configparser
from datetime import datetime

visited = set()

first_request_received = False
start = datetime.now()
end = datetime.now()

config = configparser.ConfigParser()
config.read('crawler.cfg')
HOST = config['server']['host']
PORT = int(config['server']['port'])

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('', PORT))
soc.listen()
print("Listening on port %s... Press CTRL+C to quit" % PORT)

try:
	while True:
		conn, addr = soc.accept()
		url = conn.recv(1024).decode()
		res = "Y" if url in visited else "N"
		visited.add(url)
		conn.sendall(res.encode())
		conn.close()
		#get timings
		if first_request_received == False:
			first_request_received = True
			start = datetime.now()
		end = datetime.now()

except KeyboardInterrupt:
	soc.close()
	print("\nSocket on port %s closed.\n%d pages founded in %s seconds.\nThis program will end in 5 seconds..." % (PORT, len(visited), (end-start).total_seconds()))
	time.sleep(5)

