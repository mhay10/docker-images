# vpnstatus

An asynchronous microservice built with Quart and Hypercorn that queries an upstream VPN control API (such as Gluetun), aggregates network status, and exposes health and connection state over HTTP.

## Features

* **Parallel Upstream Fetching**: Requests public IP, forwarded port, and tunnel status concurrently using `aiohttp`.
* **In-Memory Caching**: Caches aggregated VPN responses for 15 seconds to minimize request overhead on the VPN daemon.
* **Connection Probes**: Exposes dedicated endpoints for container health checks, reverse proxy status checks, and detailed JSON reporting.

## Environment Variables

| Variable   | Description                                               | Default     |
| :--------- | :-------------------------------------------------------- | :---------- |
| `VPN_HOST` | Hostname or IP address of the upstream VPN control server | `localhost` |
| `VPN_PORT` | Port number of the upstream VPN control server            | `8000`      |

## API Endpoints

### 1. `GET /health`

Basic service liveness check.

* **Response Code**: `200 OK`
* **Payload**:

```json
{
  "status": "ok"
}
```

### 2. `GET /vpn-status`

Returns the cached or freshly retrieved status from the upstream VPN server.

* **Success Response Code**: `200 OK`
* **Failure Response Code**: `503 Service Unavailable` (if any upstream query fails or times out)
* **Success Payload**:

  ```json
  {
    "public_ip": "198.51.100.42",
    "forwarded_port": "51820",
    "status": "running"
  }
  ```

* **Error Payload**:

  ```json
  {
    "error": "Upstream errors: HTTP Error: ..."
  }
  ```

### 3. `GET /vpn-connected`

Binary health check designed for reverse proxies, routing gates, or container orchestration health checks.

* **Response Code**: `200 OK` if upstream `status` equals `running`.
* **Response Code**: `503 Service Unavailable` if upstream status is not running or unreachable.
* **Payload**: Empty body.

## Upstream API Dependencies

The application expects the upstream host (`http://$VPN_HOST:$VPN_PORT`) to expose the following endpoints:

* `GET /v1/publicip/ip`: Expects JSON containing key `public_ip`.
* `GET /v1/portforward`: Expects JSON containing key `port`.
* `GET /v1/vpn/status`: Expects JSON containing key `status`.

## Deployment

The service binds to `0.0.0.0:4000` and runs on Python 3.14-slim.

### Build and Run Manually

Build the image:

```bash
docker build -t vpnstatus .
```

Run container:

```bash
docker run -d \
  --name vpnstatus \
  -p 4000:4000 \
  -e VPN_HOST="192.168.1.100" \
  -e VPN_PORT="8000" \
  vpnstatus
```

### Docker Compose

```yaml
services:
  vpnstatus:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vpnstatus
    network_mode: "container:gluetun"
    environment:
      - VPN_HOST=localhost  # The Gluetun control server ip/hostname
      - VPN_PORT=8000       # The Gluetun control server port
    ports:
      - 4000:4000
    restart: unless-stopped
```
