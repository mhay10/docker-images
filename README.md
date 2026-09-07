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

IMages are built and published to the GitHub Container Registry (`ghcr.io`) via GitHub Actions:

* **Caddy Workflow** (`build-caddy.yml`): Triggers on tags matching `caddy-v*` or manaully.
* **VPN Status Workflow** (`build-vpnstatus.yml`): Triggers on tags matching `vpnstatus-v*` or manaully.

Both workflows handle image tagging via `docker/metadata-action`:
* **Tagged releases**: Strips the prefix (`caddy-v1.2.3` -> `1.2.3`), updates the `latest` tag, and pushes to `ghcr.io`.
* **Manual runs**: Tags the build with the short commit SHA and pushes to `ghcr.io`.