# docker-images

A monorepo containing custom Docker image definitions, configurations, and automated build pipelines.

## Images Overview

| Image | Directory | Base Image | Built Features / Dependencies |
| --- | --- | --- | --- |
| **caddy** | `/caddy` | `caddy:alpine` | Compiled via `xcaddy` with the [Caddy Clouflare module](https://github.com/caddy-dns/cloudflare) for DNS-01 challenges |
| **vpnstatus** | `/vpnstatus` | `python:3.14-slim` | Quart, Hypercorn, and aiohttp for parallel upstream Gluetun VPN probing and caching |

## Image Details

### 1. Caddy (`/caddy`)

A custom build of the official Caddy Alpine image that bundles the Cloudflare DNS module using a multi-stage `xcaddy` builder. It facilitates automatic TLS certificate procurement via Let's Encrypt and ZeroSSL using DNS-01 verification without requiring public HTTP/HTTPS ports to be reachable.

* **Primary Use Case**: Reverse proxying internal infrastructure, handling wildcard SSL/TLS domains, and edge routing.
* **Documentation**: See `caddy/README.md` for Caddyfile patterns and runtime configurations.

### 2. VPN Status (`/vpnstatus`)

An asynchronous ASGI microservice running on Python 3.14 and served with Hypercorn. It interfaces with a Gluetun VPN's API to aggregate connection status, assigned public IP, and forwarded ports concurrently with built-in 15-second response caching.

* **Listening Port**: `4000`
* **Key Endpoints**:
  * `GET /vpn-status`: Full JSON diagnostic report.
  * `GET /vpn-connected`: Binary `200` or `503` status gate for proxy routing.
  * `GET /health`: Microservice liveness probe.
* **Documentation**: See `vpnstatus/README.md` for environment variables, mock payloads, and integration instructions.

## CI/CD Automation

Each container directory is tracked and built independently through GitHub Actions:

* **Caddy Workflow** (`build-caddy.yml`): Triggers on modifications within the `caddy/` directory.
* **VPN Status Workflow** (`build-vpnstatus.yml`): Triggers on modifications within the `vpnstatus/` directory.

Both workflows manage automated image tagging, multi-platform builds, and registry publication.
