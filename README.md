# <img width="24px" src="./images/logo.png"></img> proxy-router 

* [What is proxy-router?](#what-is-proxy-router)
* [Why use this?](#why-use-this)
* [How it works](#how-it-works)
* [Configuration](#configuration)
  * [Authentication](#authentication)
  * [Proxies](#proxies)
  * [Routing](#routing)
* [Running the proxy](#running-the-proxy)
  * [Docker Compose (recommended)](#docker-compose-recommended)
  * [Docker CLI](#docker-cli)
* [Environment variables](#environment-variables)
* [Configure tools to use the proxy](#configure-tools-to-use-the-proxy)
* [Updating credentials](#updating-credentials)

## What is proxy-router?
A lightweight HTTP proxy server that automatically routes requests to the appropriate proxy based on hostname patterns, 
handling authentication headers dynamically.

<img width="100%" src="./images/workflow.png"></img>

## Why use this?
If your working environment uses multiple HTTP proxies with different authentication credentials for different
hostnames, managing passwords across tools can be tedious: every password rotation requires manual updates everywhere, 
leading to broken workflows, hardcoded secrets, and wasted time. This solution:  
- **Centralizes authentication**: Update passwords in one place instead of every tool.  
- **Automates routing**: Routes requests to the correct proxy using wildcard hostname matching (e.g., `*.my-company-domain.com`).  
- **Simplifies maintenance**: Setup proxies and credentials via configuration files.  

## How it works
1. **Intercepts requests** from your tools (e.g., `curl`, `npm`, `git`).  
2. **Matches the hostname** against configured patterns to select the right proxy.  
3. **Adds Basic Authentication headers** with the proxy’s credentials.  
4. **Forwards the request** to the target proxy.

## Configuration
### Authentication
Edit [auth.json](./resources/auth.json) to define your different authentication credentials.
```json
[
  {
      "id": "company-user",
      "username": "company-username",
      "password": "company-password"
    },
    {
      "id": "internet-user",
      "username": "internet-username",
      "password": "internet-password"
    }
]
```

### Proxies
Edit [proxy.json](./resources/proxy.json) to define your list of proxies. The `authenticationId` property of each proxy 
has to point to an existing authentication method in [auth.json](./resources/auth.json) file.
```json
[
  {
    "id": "company-proxy",
    "hostname": "pxy-company.my-company-domain.com",
    "port": 3128,
    "authenticationId": "company-user"
  },
  {
    "id": "external-proxy",
    "hostname": "pxy-external.my-company-domain.com",
    "port": 3128,
    "authenticationId": "company-user"
  },
  {
    "id": "internet-proxy",
    "hostname": "pxy-internet.my-company-domain.com",
    "port": 3128,
    "authenticationId": "internet-user"
  }
]
```

### Routing
Edit [routing.json](./resources/routing.json) to define your request hostname patterns and the proxies to point to. The 
`proxyId` field of each routing rule has to point to an existing proxy in [proxy.json](./resources/proxy.json) file.
```json
[
  {
    "requestHostnamePattern": "*.my-company-domain.com",
    "proxyId": "company-proxy"
  },
  {
    "requestHostnamePattern": "*.external-domain.com",
    "proxyId": "external-proxy"
  },
  {
    "requestHostnamePattern": "pxy-internet.my-company-domain.com",
    "proxyId": "internet-proxy"
  }
]
```

## Running the proxy
### Docker Compose (recommended)
```yaml
services:
  proxy-router:
    container_name: proxy-router
    image: proxy-router
    ports:
      - "8888:8888"
    restart: unless-stopped
    volumes:
      - ./secrets/auth.json:/app/auth.json
      - ./secrets/routing.json:/app/routing.json
      - ./secrets/proxy.json:/app/proxy.json
```

### Docker CLI
```bash
docker run -d \
  --name proxy-router \
  -p 8888:8888 \
  --restart=unless-stopped \
  -v ./secrets/auth.json:/app/auth.json \
  -v ./secrets/routing.json:/app/routing.json \
  -v ./secrets/proxy.json:/app/proxy.json \
  proxy-router
```

## Environment variables
|           **Variable**           |    **Default**    | **Description**                                       |
|:--------------------------------:|:-----------------:|:------------------------------------------------------|
|         `LOGGING_LEVEL`          |       INFO        | Logging level of the proxy                            |
|     `AUTH_CONFIG_FILE_PATH`      |  /app/auth.json   | Path to the authentication configuration file         |
|    `ROUTING_CONFIG_FILE_PATH`    | /app/routing.json | Path to the routing rules configuration file          |
|     `PROXY_CONFIG_FILE_PATH`     |  /app/proxy.json  | Path to the proxies configuration file                |
| `PROXY_SERVER_BUFFER_SIZE_BYTES` |       4096        | Buffer size in bytes of each streaming request reader |
|       `PROXY_SERVER_HOST`        |      0.0.0.0      | Hostname that the proxy will be bound to              |
|       `PROXY_SERVER_PORT`        |       8888        | Port that the proxy will listen to                    |
|  `PROXY_SERVER_TIMEOUT_SECONDS`  |        2.0        | Time in seconds to shutdown unused connections        |

## Configure tools to use the proxy
Set your tools to use the proxy address, by default `http://localhost:8888`. 
For example:  
- **git**:  
  ```bash
  git config --global http.proxy http://localhost:8888
  ```  
- **npm**:  
  ```bash
  npm config set proxy http://localhost:8888
  ```  
- **curl**:  
  ```bash
  export http_proxy=http://localhost:8888
  ```  

## Updating credentials
Just change the passwords in [auth.json](./resources/auth.json) configuration file. 

No need to update individual tools!  
