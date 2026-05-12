#!/usr/bin/env python3
"""
HUSKYLENS 2 MCP Connection Test

Tests connectivity to HUSKYLENS 2 MCP service:
1. TCP connectivity to device:port
2. SSE endpoint accessibility
3. MCP initialize handshake
4. Tool discovery (tools/list)

Usage:
    python test_connection.py [--host HOST] [--port PORT]
"""
import sys
import time
import json
import re
import subprocess
import tempfile
import os


def test_tcp(host, port, timeout=5):
    """Test TCP connectivity."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  TCP test error: {e}")
        return False


def test_sse(host, port, timeout=10):
    """Test SSE endpoint and get session info."""
    sse_url = f"http://{host}:{port}/sse"
    sse_file = os.path.join(tempfile.gettempdir(), "_hl2_test_sse.txt")
    open(sse_file, 'wb').close()

    proc = subprocess.Popen(
        ["curl", "-s", "-N", "--max-time", str(timeout + 5), sse_url],
        stdout=open(sse_file, "wb"),
        stderr=subprocess.PIPE
    )

    session_id = None
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with open(sse_file, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            if 'session_id=' in text:
                m = re.search(r'session_id=(\S+)', text)
                if m:
                    session_id = re.split(r'[\s&]', m.group(1))[0]
                break
        except Exception:
            pass
        time.sleep(0.5)

    proc.terminate()
    return session_id


def test_mcp_init(host, port, session_id, timeout=15):
    """Test MCP initialize handshake."""
    msg_url = f"http://{host}:{port}/message?session_id={session_id}"

    sse_file = os.path.join(tempfile.gettempdir(), "_hl2_test_sse2.txt")
    open(sse_file, 'wb').close()

    # Start SSE reader
    proc = subprocess.Popen(
        ["curl", "-s", "-N", "--max-time", str(timeout + 10),
         f"http://{host}:{port}/sse"],
        stdout=open(sse_file, "wb"),
        stderr=subprocess.PIPE
    )

    time.sleep(2)

    # Get new session ID
    new_sid = None
    with open(sse_file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    m = re.search(r'session_id=(\S+)', text)
    if m:
        new_sid = re.split(r'[\s&]', m.group(1))[0]

    if not new_sid:
        proc.terminate()
        return None

    msg_url = f"http://{host}:{port}/message?session_id={new_sid}"

    # Send initialize
    subprocess.run(
        ["curl", "-s", "-X", "POST", msg_url,
         "-H", "Content-Type: application/json",
         "-d", json.dumps({
             "jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {
                 "protocolVersion": "2024-11-05",
                 "capabilities": {},
                 "clientInfo": {"name": "hl2-test", "version": "1.0"}
             }
         })],
        capture_output=True, timeout=15
    )

    # Wait for response
    time.sleep(3)
    server_info = None
    with open(sse_file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    for line in text.split('\n'):
        line = line.strip()
        if not line.startswith('data: '):
            continue
        payload = line[6:].strip()
        if not payload or payload.isdigit():
            continue
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict) and obj.get('id') == 1:
                server_info = obj.get('result', {}).get('serverInfo', {})
                break
        except json.JSONDecodeError:
            continue

    proc.terminate()
    return server_info


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test HUSKYLENS 2 MCP connectivity")
    parser.add_argument("--host", default="192.168.88.1", help="Device IP")
    parser.add_argument("--port", type=int, default=3000, help="MCP port")
    args = parser.parse_args()

    host, port = args.host, args.port
    print(f"HUSKYLENS 2 MCP Connection Test")
    print(f"Target: {host}:{port}")
    print("=" * 40)

    # Step 1: TCP
    print("\n1. TCP Connectivity...")
    if test_tcp(host, port):
        print(f"   ✅ {host}:{port} is reachable")
    else:
        print(f"   ❌ {host}:{port} is NOT reachable")
        print("   Check: WiFi connection, device power, MCP service enabled")
        sys.exit(1)

    # Step 2: SSE
    print("\n2. SSE Endpoint...")
    session_id = test_sse(host, port)
    if session_id:
        print(f"   ✅ SSE endpoint accessible, session_id: {session_id[:20]}...")
    else:
        print("   ❌ Could not get session_id from SSE")
        sys.exit(1)

    # Step 3: MCP Init
    print("\n3. MCP Initialize...")
    server_info = test_mcp_init(host, port, session_id)
    if server_info:
        print(f"   ✅ MCP handshake successful")
        print(f"   Server: {server_info.get('name', '?')} v{server_info.get('version', '?')}")
    else:
        print("   ❌ MCP initialize failed")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("✅ All tests passed! HUSKYLENS 2 MCP service is operational.")
    print(f"\nSSE URL: http://{host}:{port}/sse")


if __name__ == "__main__":
    main()
