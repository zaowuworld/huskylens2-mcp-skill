#!/usr/bin/env python3
"""
HUSKYLENS 2 MCP Connection Tester

Tests connectivity to HUSKYLENS 2 MCP service via SSE endpoint.

Usage:
    python test_connection.py [--host HOST] [--port PORT] [--timeout SECONDS]

Defaults:
    --host 192.168.88.1
    --port 3000
    --timeout 5
"""
import argparse
import json
import sys


def test_http_connection(host, port, timeout):
    """Test basic HTTP connectivity to the MCP service."""
    import urllib.request
    import urllib.error

    url = f"http://{host}:{port}/sse"
    print(f"Testing connection to {url} ...")

    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "text/event-stream")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            headers = dict(resp.headers)
            print(f"  Status: {status}")
            print(f"  Content-Type: {headers.get("Content-Type", "unknown")}")
            # Read a small chunk to confirm SSE stream
            chunk = resp.read(1024).decode("utf-8", errors="replace")
            print(f"  Received data: {len(chunk)} bytes")
            if "event" in chunk.lower() or "data" in chunk.lower():
                print("  SSE stream detected: OK")
            return True
    except urllib.error.URLError as e:
        print(f"  Connection FAILED: {e.reason}")
        return False
    except Exception as e:
        print(f"  Connection FAILED: {e}")
        return False


def test_tcp_connection(host, port, timeout):
    """Test basic TCP connectivity."""
    import socket
    print(f"Testing TCP connection to {host}:{port} ...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print("  TCP connection: OK")
            return True
        else:
            print(f"  TCP connection FAILED (errno={result})")
            return False
    except socket.timeout:
        print("  TCP connection FAILED: timeout")
        return False
    except Exception as e:
        print(f"  TCP connection FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test HUSKYLENS 2 MCP connectivity")
    parser.add_argument("--host", default="192.168.88.1", help="HUSKYLENS 2 IP address")
    parser.add_argument("--port", type=int, default=3000, help="MCP service port")
    parser.add_argument("--timeout", type=int, default=5, help="Connection timeout in seconds")
    args = parser.parse_args()

    print(f"=== HUSKYLENS 2 MCP Connection Test ===")
    print(f"Target: {args.host}:{args.port}")
    print()

    tcp_ok = test_tcp_connection(args.host, args.port, args.timeout)
    print()

    if tcp_ok:
        http_ok = test_http_connection(args.host, args.port, args.timeout)
        print()

        if http_ok:
            print("Result: HUSKYLENS 2 MCP service is reachable and responding.")
            print(f"SSE URL: http://{args.host}:{args.port}/sse")
        else:
            print("Result: TCP connection OK but MCP service not responding properly.")
            print("Check that MCP service is enabled on HUSKYLENS 2.")
    else:
        print("Result: Cannot reach HUSKYLENS 2.")
        print("Troubleshooting:")
        print("  1. Ensure HUSKYLENS 2 is powered on")
        print("  2. Ensure WiFi is connected (or use AP mode IP)")
        print("  3. Ensure MCP service is enabled on device")
        print("  4. Ensure your computer is on the same network")
        print("  5. Try pinging the device: ping", args.host)

    return 0 if tcp_ok else 1


if __name__ == "__main__":
    sys.exit(main())
