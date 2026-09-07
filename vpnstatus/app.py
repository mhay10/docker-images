import asyncio
import json
import os
import time
from typing import Any

import aiohttp
from aiohttp import ClientSession
from quart import Quart, Response, jsonify

from hypercorn.config import Config
from hypercorn.asyncio import serve

# API Server Details
app = Quart(__name__)
SERVER_PORT = 4000

# VPN Server Details
VPN_HOST = os.environ.get("VPN_HOST", "localhost")
VPN_PORT = os.environ.get("VPN_PORT", "8000")
VPN_BASE_URL = f"http://{VPN_HOST}:{VPN_PORT}"

# Cache
CACHE_TTL = 15
_cache: dict[str, dict[str, str]] = {}
_cache_time: dict[str, float] = {}

# ==== HELPER METHODS ====


async def get_vpn_endpoint(session: ClientSession, endpoint: str) -> dict[str, Any]:
    """Fetch a single endpoint from VPN API

    Makes an async HTTP GET request to the provided VPN API endpoint and
    returns the JSON response. On an error, a dict with the `error` key
    is returned containin the error message

    :param session: Active aiohttp session for making the request
    :param endpoint: VPN API endpoint (e.g. "/v1/publicip/ip")

    :returns: JSON response as dict or {"error": "error message"} on failure
    """

    try:
        async with session.get(
            f"{VPN_BASE_URL}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)
        ) as response:
            response.raise_for_status()

            text = await response.text()
            return json.loads(text)

    except aiohttp.ClientError as e:
        return {"error": f"HTTP Error: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"error": str(e)}


async def get_vpn_data_cached() -> tuple[dict[str, str] | None, str | None]:
    """Fetch all VPN data in parallel with caching

    Combines data from 3 different API endpoints (public IP, forwarded port,
    and connection status) in parallel. Results are cached for `CACHE_TTL` seconds
    to reduce API load.

    :returns: Tuple of (data_dict, error_str)
        - `data_dict` - Is None on error, or else contains `public_ip`, `forwarded_port`, and `status`
        - `error_str` - Is none on success, or else contains error message(s)
    """
    now = time.time()

    # Return cached result if fresh
    if "vpn_data" in _cache and (now - _cache_time.get("vpn_data", 0)) < CACHE_TTL:
        return _cache["vpn_data"], None

    try:
        async with aiohttp.ClientSession() as session:
            # Fetch all three endpoints in parallel
            ip_task = get_vpn_endpoint(session, "/v1/publicip/ip")
            port_task = get_vpn_endpoint(session, "/v1/portforward")
            status_task = get_vpn_endpoint(session, "/v1/vpn/status")

            ip_data, port_data, status_data = await asyncio.gather(
                ip_task,
                port_task,
                status_task,
            )

        # Check for errors in any response
        if any(d.get("error") for d in [ip_data, port_data, status_data]):
            errors = [
                d.get("error")
                for d in [ip_data, port_data, status_data]
                if d.get("error")
            ]
            return None, f"Upstream errors: {', '.join(errors)}"

        # Format, cache, and return results
        result = {
            "public_ip": ip_data.get("public_ip", "N/A"),
            "forwarded_port": port_data.get("port", "N/A"),
            "status": status_data.get("status", "N/A"),
        }

        _cache["vpn_data"] = result
        _cache_time["vpn_data"] = now

        return result, None

    except Exception as e:
        return None, str(e)


# ==== API ROUTES ====


@app.route("/vpn-status", methods=["GET"])
async def vpn_status() -> tuple[Response, int]:
    data, error = await get_vpn_data_cached()
    if error:
        return jsonify({"error": error}), 503
    return jsonify(data), 200


@app.route("/vpn-connected", methods=["GET"])
async def vpn_connected() -> tuple[Response, int]:
    data, error = await get_vpn_data_cached()
    if error:
        return "", 503
    is_connected = data.get("status", "").lower() == "running"
    return "", 200 if is_connected else 503


@app.route("/health", methods=["GET"])
async def health() -> tuple[Response, int]:
    """Basic health check"""
    return jsonify({"status": "ok"}), 200


# ==== API ASGI SERVING ====

if __name__ == "__main__":
    config = Config()
    config.bind = f"0.0.0.0:{SERVER_PORT}"
    asyncio.run(serve(app, config))
