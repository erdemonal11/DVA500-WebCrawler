# DVA500-WebCrawler

[DVA500: Industriella system i datamoln](https://www.mdu.se/utbildning/kurser?kod=DVA500) – WebCrawler is a containerized web crawler that autonomously explores the internet, fetching HTML pages and extracting links while ensuring each page is visited only once. Built on a client-server architecture, it is designed for efficiency and ease of use, making it ideal for data extraction and web analysis.

## Architecture Diagram

![Architecture Diagram](images/structure.png)

This diagram shows the interaction between clients and the server, where clients fetch HTML pages, check with the server to avoid revisiting, and extract links for further exploration.

## Features

- Client-server architecture for efficient URL management.
- Retry mechanism for handling failed HTTP requests.
- Prevents visiting already crawled URLs to optimize performance.
- Containerized environment for easy deployment and scalability.

## Requirements

- Docker
- Python 3.9 or later
- Required Python packages will be installed automatically via Docker.

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/erdemonal11/DVA500-WebCrawler.git
   cd DVA500-WebCrawler
   
2. **Build and run the web server**
    ```bash
    make create_web
    
3. **Run the server**
    ```bash
    make run_server
    
4. **Run the clients:**
   You can specify the number of client instances to run
    ```bash
    make run_clients n=2

## View Execution Times

After running the clients, you can check the `execution_times.log` file for performance metrics:

```bash
cat execution_times.log
```

## Configuration

The configuration for the server can be found in the `crawler.cfg` file. Modify the host and port settings as needed to suit your environment.

## Cleaning Up

To stop and remove all containers, use the following commands:

```bash
make stop_all
make remove_network
```

## Acknowledgments

- Inspired by concepts in web crawling and distributed systems.
- Uses [requests](https://docs.python-requests.org/en/latest/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for HTTP requests and HTML parsing.

## Detailed Analysis Report

For a comprehensive overview of the project's findings and performance metrics, please refer to the detailed analysis report below:

[LAB1 G7 Report.pdf](https://github.com/user-attachments/files/17606721/LAB1.G7.Report.pdf)



    
