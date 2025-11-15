basename=$(shell docker inspect --format='{{.NetworkSettings.Networks.crawlernet.Gateway}}' webserver)
n ?= 2
LOG_LEVEL ?= INFO

.PHONY: run_clients clean surf install run_server create_web stop_all remove_network build_client

surf:
	@google-chrome --incognito http://$(basename):8080 2> /dev/null

build_client:
	@echo "Building client image..."
	@docker build -f Dockerfile.client -t my-crawler-client .

run_server:
	@echo "Starting server..."
	@docker image inspect my-crawler-server >/dev/null 2>&1 || docker build -f Dockerfile.server -t my-crawler-server .
	@docker rm -f my-crawler-server-container 2>/dev/null || true
	@docker run --network crawlernet -p 8015:8015 --name my-crawler-server-container -e LOG_LEVEL=$(LOG_LEVEL) -it my-crawler-server

run_clients:
	@docker image inspect my-crawler-client >/dev/null 2>&1 || docker build -f Dockerfile.client -t my-crawler-client .
	@echo "Running $(n) processes..."
	@rm -f execution_times.log
	@for i in $(shell seq 1 $(n)); do \
		docker rm -f my-crawler-client-$$i 2>/dev/null || true; \
		start_time=$$(date +%s%N); \
		docker run --network crawlernet --name my-crawler-client-$$i --env PROCESS_ID=$$i -e LOG_LEVEL=$(LOG_LEVEL) my-crawler-client $$i http://webserver:80/page_$$i.html & \
		wait; \
		end_time=$$(date +%s%N); \
		execution_time=$$(awk "BEGIN {printf \"%.5f\", ($$end_time - $$start_time) / 1000000000}"); \
		echo "Process $$i, Execution Time: $$execution_time seconds" >> execution_times.log; \
	done
	@echo "Execution times logged in execution_times.log"

.PHONY: logs_server logs_client-%
logs_server:
	@docker logs -f my-crawler-server-container

logs_client-%:
	@docker logs -f my-crawler-client-$*

create_web:
	@docker network inspect crawlernet >/dev/null 2>&1 || docker network create --driver bridge crawlernet
	@docker rm -f webserver 2>/dev/null || true
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

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

precommit:
	poetry run pre-commit run --all-files

test:
	poetry run pytest -q

docs:
	poetry run sphinx-build -b html docs/source docs/_build/html
	@echo "Documentation built in docs/_build/html"
