"""
LabhArth AI — Network Diagnostics Script
===========================================
Diagnoses local network reachability to Neon PostgreSQL and Qdrant Cloud.
Checks if ports 5432, 6333, and 443 are blocked, and fetches the external IP
to assist in Neon/Qdrant IP whitelist troubleshooting.
"""

import asyncio
import socket
import urllib.request
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.utils.config import get_settings


def get_external_ip():
    """Fetch external IP address."""
    try:
        url = "https://api.ipify.org"
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        return f"Unknown (Failed to fetch: {e})"


async def test_tcp_connect(host: str, port: int, name: str) -> bool:
    """Test standard TCP connection to a host and port."""
    print(f"Testing TCP connection to {name} ({host}:{port})...")
    try:
        # Resolve hostname
        loop = asyncio.get_event_loop()
        addr_info = await loop.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        ip = addr_info[0][4][0]
        print(f"  - Resolved {host} to {ip}")
        
        # Connect socket
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        print(f"  - ✅ Connection to {name} SUCCEEDED!")
        return True
    except asyncio.TimeoutError:
        print(f"  - ❌ Connection to {name} TIMED OUT (Blocked by firewall or wrong port).")
        return False
    except Exception as e:
        print(f"  - ❌ Connection to {name} FAILED: {e}")
        return False


async def main():
    settings = get_settings()
    print("=" * 60)
    print(" LABHARTH AI — NETWORK DIAGNOSTICS")
    print("=" * 60)
    
    # 1. Check External IP
    print("\n[1] Checking Local Environment:")
    ext_ip = get_external_ip()
    print(f"  - Current External IP: {ext_ip}")
    print("  * If you have set up Neon or Qdrant IP Allow Lists, verify that this IP is whitelisted.")

    # 2. Parse database URL host/port
    print("\n[2] Checking Neon PostgreSQL Connection:")
    db_url = settings.database_url
    # Extract host
    host = "localhost"
    port = 5432
    if "@" in db_url:
        host_part = db_url.split("@")[1].split("/")[0]
        if ":" in host_part:
            host, port_str = host_part.split(":")
            port = int(port_str.split("?")[0])
        else:
            host = host_part.split("?")[0]
            port = 5432
    
    db_ok = await test_tcp_connect(host, port, "Neon PostgreSQL")

    # 3. Parse Qdrant host/port
    print("\n[3] Checking Qdrant Cloud Connection:")
    q_url = settings.qdrant_url
    q_host = "localhost"
    q_port = 6333
    
    if q_url.startswith("https://"):
        q_host = q_url[8:]
        q_port = 443  # default https
    elif q_url.startswith("http://"):
        q_host = q_url[7:]
        q_port = 80
        
    if ":" in q_host:
        q_host, port_str = q_host.split(":")
        q_port = int(port_str)

    qdrant_ok = await test_tcp_connect(q_host, q_port, "Qdrant Cloud")

    print("\n" + "=" * 60)
    print(" SUMMARY:")
    print(f"  - PostgreSQL reachable: {'YES' if db_ok else 'NO'}")
    print(f"  - Qdrant Cloud reachable: {'YES' if qdrant_ok else 'NO'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
