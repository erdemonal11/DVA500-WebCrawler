basename=$(shell docker inspect --format='{{.NetworkSettings.Networks.crawlernet.Gateway}}' webserver)
n ?= 2  

.PHONY: run_clients clean surf install run_server create_web stop_all remove_network build_client

surf:
	@google-chrome --incognito http://$(basename):8080 2> /dev/null

build_client:
	@echo "Building client image..."
	@docker build -f Dockerfile.client -t my-crawler-client .

run_server:
	@echo "Starting server..."
	@docker rm -f my-crawler-server-container 2>/dev/null || true
	@docker build -f Dockerfile.server -t my-crawler-server .
	@docker run --network crawlernet -p 8015:8015 --name my-crawler-server-container -it my-crawler-server

run_clients: build_client
	@echo "Running $(n) processes..."
	@rm -f execution_times.log  
	@for i in $(shell seq 1 $(n)); do \
		docker rm -f my-crawler-client-$$i 2>/dev/null || true; \
		start_time=$$(date +%s%N); \
		docker run --network crawlernet --name my-crawler-client-$$i --env PROCESS_ID=$$i my-crawler-client $$i http://webserver:80/page_$$i.html & \
		wait; \
		end_time=$$(date +%s%N); \
		execution_time=$$(awk "BEGIN {printf \"%.5f\", ($$end_time - $$start_time) / 1000000000}"); \
		echo "Process $$i, Execution Time: $$execution_time seconds" >> execution_times.log; \
	done
	@echo "Execution times logged in execution_times.log"

create_web:
	@docker rm -v -f $(docker ps -qa) 2> /dev/null || true
	@docker system prune -a --volumes -f
	@docker network create --driver bridge crawlernet
	@docker run --name webserver -v ./html:/usr/share/nginx/html:ro --network crawlernet -p 8080:80 -d nginx:stable-alpine
	@docker inspect --format='{{.NetworkSettings.Networks.crawlernet.Gateway}}' webserver

stop_all:
	@docker stop webserver 2>/dev/null || true
	@docker rm -v webserver 2>/dev/null || true

remove_network:
	@docker network rm crawlernet 2>/dev/null || true

clean_all:
	@echo "Stopping and removing all containers..."
	@docker rm -f $(docker ps -aq) 2>/dev/null || true

install:
	poetry install

build:
	poetry build
