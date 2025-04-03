# <img width="24px" src="./images/logo.png"></img> ProxyRouter 
## Smart Proxy Router with Dynamic Authentication
### The problem:

In working environments with multiple authenticated proxies (e.g., split by hostname), managing credentials across tools
(curl, browsers, scripts, etc.) is painful: every password rotation requires manual updates everywhere, leading to 
broken workflows, hardcoded secrets, and wasted time.

### The solution:
A lightweight Python proxy server that:
1. **Routes requests intelligently** – Matches hostnames (supports wildcards like *.domain.com) to the correct proxy.
2. **Injects authentication dynamically** - Adds Basic Authentication headers, so credentials are managed in one place.
3. **Simplifies maintenance** - Change passwords once in the config; no more hunting down proxy settings across tools.

### Use cases:
- Developers tired of reconfiguring proxies in every IDE / CLI tool.
- Scripts / automation that rely on authenticated proxies.
- Teams enforcing frequent password rotations without the hassle.

<img width="100%" src="./images/workflow.png"></img>
