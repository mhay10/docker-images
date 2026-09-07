# caddy

Custom Caddy Docker image based on Alpine Linux, built with the `github.com/caddy-dns/cloudflare` plugin compiled via `xcaddy`. This enables Caddy to solve DNS-01 ACME challenges to acquire Let's Encrypt or ZeroSSL TLS certificates for wildcard domains or internal servers not exposed to ports 80/443.

## Build Architecture

The image uses a multi-stage Docker build:

* **Builder**: `caddy:builder-alpine` compiling the custom binary via `xcaddy build --with github.com/caddy-dns/cloudflare`.
* **Runtime**: `caddy:alpine` containing the compiled binary copied to `/usr/bin/caddy`.

## Configuration

To use the Cloudflare DNS provider for ACME challenges, supply a Cloudflare API token with `Zone.DNS:Edit` permissions.

### Example `Caddyfile`

```caddyfile
example.com, *.example.com {
    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }

    reverse_proxy localhost:8080
}
```

## Deployment

### Docker Compose

```yaml
services:
  caddy:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp" # HTTP/3
    environment:
      - CLOUDFLARE_API_TOKEN=your_api_token_here
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

### Docker CLI

Build image:

```bash
docker build -t caddy-cloudflare .
```

Run container:

```bash
docker run -d \
  --name caddy \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -p 443:443/udp \
  -e CLOUDFLARE_API_TOKEN="your_api_token_here" \
  -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v caddy_data:/data \
  -v caddy_config:/config \
  caddy-cloudflare
```
