"""Quick database connection diagnostic.

Run from the backend/ directory:
    python scripts/test_connection.py

Checks DNS resolution, TCP reachability, and SQLAlchemy connectivity.
Never prints credentials.
"""
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

backend_root = Path(__file__).resolve().parents[1]
os.chdir(backend_root)
sys.path.insert(0, str(backend_root))


def _mask(url: str) -> str:
    """Return the URL with password replaced by ***."""
    parsed = urlparse(url)
    if parsed.password:
        masked = parsed._replace(netloc=f"{parsed.username}:***@{parsed.hostname}:{parsed.port}")
        return masked.geturl()
    return url


def main() -> int:
    from app.core.config import get_settings

    settings = get_settings()
    url = settings.database_url
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or 5432

    print(f"target  : {_mask(url)}")
    print(f"driver  : {parsed.scheme}")
    print(f"host    : {host}")
    print(f"port    : {port}")
    print()

    # --- DNS ---
    print("[1/3] DNS resolution …")
    try:
        addrs = socket.getaddrinfo(host, port)
        families = {a[0] for a in addrs}
        ipv4 = socket.AF_INET in families
        ipv6 = socket.AF_INET6 in families
        print(f"  [OK] resolved ({len(addrs)} records, IPv4={ipv4}, IPv6={ipv6})")
    except socket.gaierror as exc:
        print(f"  [FAIL] {exc}")
        print()
        print("FIX: Your Supabase project uses an IPv6-only direct hostname.")
        print("     Switch to the Session-mode pooler connection string from")
        print("     Supabase Dashboard -> Project Settings -> Database -> Connection pooling.")
        return 1

    # --- TCP ---
    print("[2/3] TCP connectivity ...")
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        print("  [OK] TCP connection succeeded")
    except OSError as exc:
        print(f"  [FAIL] {exc}")
        return 1

    # --- SQLAlchemy ---
    print("[3/3] SQLAlchemy connection ...")
    try:
        from sqlalchemy import text
        from app.core.database import engine

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
        print("  [OK] SQLAlchemy query succeeded")
    except Exception as exc:
        msg = str(exc)
        # Scrub any password that might appear in the exception message
        if parsed.password and parsed.password in msg:
            msg = msg.replace(parsed.password, "***")
        print(f"  [FAIL] {msg}")
        return 1

    print()
    print("ALL CHECKS PASSED [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
