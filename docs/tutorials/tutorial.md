# WebCrawler Tutorial

This tutorial will guide you through setting up and running the DVA500-WebCrawler project.

## What is this project?

DVA500-WebCrawler is a containerized web crawler that explores the internet, fetching and linking HTML pages. It uses a client server architecture where multiple clients can crawl pages simultaneously while the server tracks which URLs have been visited.

## Prerequisites

Before you start, make sure you have the following installed:

- **Docker**: For running containers
- **Python 3.9 or later**: For development
- **Poetry**: For dependency management
- **Make**: For running commands easily

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/erdemonal11/DVA500-WebCrawler.git
cd DVA500-WebCrawler
```

### Step 2: Install dependencies

```bash
poetry install
```

This will install all required Python packages.

## Running the Web Crawler

The project uses Docker containers to run the server and clients. Follow these steps:

### Step 1: Create the web server

First, we need to set up a web server that will serve HTML pages for the crawler to visit:

```bash
make create_web
```

This command:
- Creates a Docker network called `crawlernet`
- Starts an Nginx web server
- Serves HTML files from the `html/` directory
- Makes the server accessible at `http://localhost:8080`

### Step 2: Start the crawler server

In a new terminal window, start the crawler server:

```bash
make run_server
```

The server will:
- Track which URLs have been visited
- Listen on port 8015
- Log all operations

Keep this terminal open - the server needs to keep running.

### Step 3: Run the clients

In another terminal window, run the crawler clients:

```bash
make run_clients n=2
```

This will:
- Start 2 client containers
- Each client visits a different starting URL
- Clients check with the server before visiting each page
- Execution times are logged to `execution_times.log`

You can change the number of clients by changing `n=2` to any number you want (e.g., `n=5` for 5 clients).

## Example Usage

### Running with 3 clients

```bash
make run_clients n=3
```

### Viewing execution times

After running clients, check how long each process took:

```bash
cat execution_times.log
```

### Viewing logs

To see what the server is doing:

```bash
make logs_server
```

To see what a specific client did:

```bash
make logs_client-1
```

## Stopping Everything

When you're done, clean up:

```bash
# Stop the web server
make stop_all

# Remove the network
make remove_network
```

## Troubleshooting

**Problem**: "Cannot connect to server"

**Solution**: Make sure the server is running (`make run_server`) before starting clients.

**Problem**: "Port already in use"

**Solution**: Stop any existing containers:
```bash
docker stop webserver my-crawler-server-container
docker rm webserver my-crawler-server-container
```

**Problem**: "Network not found"

**Solution**: Run `make create_web` first to create the network.

## Next Steps

- Read the [README](https://github.com/erdemonal11/DVA500-WebCrawler/blob/main/README.md) for more details
- Check the [Reference documentation](https://erdemonal11.github.io/DVA500-WebCrawler/) for code reference
- Explore the code in `webcrawler/` directory
