#!/usr/bin/env python3
"""
HUSKYLENS 2 MCP Client

Direct Python client for HUSKYLENS 2 MCP service over SSE.
Tested and verified with HUSKYLENS 2 firmware V1.1.6+.

Usage:
    python huskylens2_client.py [--host HOST] [--port PORT] <command> [args]

Commands:
    list-algorithms         List available AI algorithms
    current-algorithm       Show currently running algorithm
    switch-algorithm <name> Switch to a different algorithm (English name)
    take-photo [resolution] Take a photo (resolution: 1920x1080|1280x720|640x480)
    screenshot              Take a screenshot
    recognize [algorithm]   Get recognition results (default: current algorithm)
    device <operation>      Device control (get_backlight, get_flashlight, etc.)
    interactive             Start interactive mode

Examples:
    python huskylens2_client.py --host 192.168.1.111 list-algorithms
    python huskylens2_client.py switch-algorithm "Object Recognition"
    python huskylens2_client.py take-photo 1920x1080
    python huskylens2_client.py recognize 2
    python huskylens2_client.py interactive
"""
import argparse
import json
import sys
import os
import re
import time
import base64
import subprocess
import tempfile


class HuskyLensMCPClient:
    """Client for HUSKYLENS 2 MCP service over SSE with JSON-RPC 2.0."""

    def __init__(self, host="192.168.88.1", port=3000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._sse_proc = None
        self._sse_file = None
        self._session_id = None

    def connect(self, timeout=10):
        """Connect to MCP service, establish SSE session."""
        self._sse_file = os.path.join(tempfile.gettempdir(), "_hl2_sse.txt")
        open(self._sse_file, 'wb').close()

        self._sse_proc = subprocess.Popen(
            ["curl", "-s", "-N", "--max-time", "90", f"{self.base_url}/sse"],
            stdout=open(self._sse_file, "wb"),
            stderr=subprocess.PIPE
        )

        # Wait for session_id
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with open(self._sse_file, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
                m = re.search(r'session_id=(\S+)', text)
                if m:
                    self._session_id = re.split(r'[\s&]', m.group(1))[0]
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not self._session_id:
            self.close()
            raise ConnectionError("Could not get session ID from SSE endpoint")

        # Initialize MCP
        msg_url = f"{self.base_url}/message?session_id={self._session_id}"
        self._post(msg_url, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hl2-client", "version": "1.0"}
            }
        })

        resp = self._wait_response(1, timeout=10)
        if resp and 'result' in resp:
            info = resp['result'].get('serverInfo', {})
            print(f"Connected to {info.get('name', '?')} v{info.get('version', '?')}")
        else:
            print("Warning: No init response, connection may be unstable")

        # Send initialized notification
        time.sleep(0.3)
        self._post(msg_url, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        time.sleep(0.3)

        return True

    def close(self):
        """Close SSE connection."""
        if self._sse_proc:
            self._sse_proc.terminate()
            self._sse_proc = None

    def _post(self, url, data):
        """Send JSON-RPC via POST."""
        try:
            r = subprocess.run(
                ["curl", "-s", "-X", "POST", url,
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps(data)],
                capture_output=True, text=True, timeout=15
            )
            return r.stdout.strip()
        except Exception as e:
            return str(e)

    def _wait_response(self, target_id, timeout=20):
        """Wait for a JSON-RPC response with matching ID from SSE stream."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with open(self._sse_file, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
            except Exception:
                time.sleep(0.5)
                continue

            for line in text.split('\n'):
                line = line.strip()
                if not line.startswith('data: ') or len(line) <= 8:
                    continue
                payload = line[6:].strip()
                if not payload or payload.isdigit():
                    continue
                # Find complete JSON object
                depth = 0
                for i, ch in enumerate(payload):
                    if ch == '{': depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                obj = json.loads(payload[:i + 1])
                                if isinstance(obj, dict) and obj.get('id') == target_id:
                                    return obj
                            except json.JSONDecodeError:
                                pass
                            break
            time.sleep(0.5)
        return None

    def _call_tool(self, tool_name, arguments, timeout=30):
        """Call an MCP tool and wait for response."""
        msg_url = f"{self.base_url}/message?session_id={self._session_id}"
        req_id = hash(tool_name) % 10000 + 100  # Generate a unique-ish ID

        self._post(msg_url, {
            "jsonrpc": "2.0", "id": req_id, "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        })

        resp = self._wait_response(req_id, timeout=timeout)
        if not resp:
            return {"error": "No response (timeout)"}

        result = resp.get('result', {})
        content = result.get('content', [])
        return content

    def list_algorithms(self):
        """List available AI algorithms."""
        content = self._call_tool("manage_applications", {"operation": "application_list"})
        for item in content:
            if item.get('type') == 'text':
                print(item['text'])
        return content

    def current_algorithm(self):
        """Show currently running algorithm."""
        content = self._call_tool("manage_applications", {"operation": "current_application"})
        for item in content:
            if item.get('type') == 'text':
                print(item['text'])
        return content

    def switch_algorithm(self, name):
        """Switch to a different algorithm."""
        content = self._call_tool("manage_applications",
                                  {"operation": "switch_application", "algorithm": name})
        for item in content:
            if item.get('type') == 'text':
                print(item['text'])
        return content

    def take_photo(self, resolution="1280x720"):
        """Take a photo. Returns filename on success."""
        content = self._call_tool("multimedia_control",
                                  {"operation": "take_photo", "resolution": resolution})
        filename = None
        for item in content:
            if item.get('type') == 'text':
                print(item['text'])
                m = re.search(r'"filename"\s*:\s*"([^"]+)"', item['text'])
                if m:
                    filename = m.group(1)
        return filename

    def take_screenshot(self):
        """Take a screenshot."""
        content = self._call_tool("multimedia_control", {"operation": "take_screenshot"})
        for item in content:
            if item.get('type') == 'text':
                print(item['text'])
        return content

    def recognize(self, algorithm=0):
        """Get recognition results."""
        content = self._call_tool("get_recognition_result",
                                  {"operation": "get_result", "algorithm": algorithm})
        for item in content:
            itype = item.get('type', '')
            if itype == 'resource_link':
                uri = item.get('uri', '')
                print(f"Image: {uri}")
            elif itype == 'text':
                print(f"Results: {item['text']}")
        return content

    def download_photo(self, filename, output_path=None):
        """Download a photo from the device."""
        if not output_path:
            output_path = filename
        url = f"{self.base_url}/photo/{filename}"
        try:
            subprocess.run(
                ["curl", "-s", "-o", output_path, "--max-time", "15", url],
                capture_output=True, timeout=20
            )
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"Downloaded: {output_path} ({size:,} bytes)")
                return output_path
        except Exception as e:
            print(f"Download failed: {e}")
        return None

    def interactive(self):
        """Start interactive mode."""
        print("HUSKYLENS 2 Interactive Client")
        print("Commands: list, current, switch <name>, photo [res], screenshot, recognize [id], download <filename>, quit")
        print()

        while True:
            try:
                cmd = input("huskylens2> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()

            if command in ("quit", "exit", "q"):
                print("Bye!")
                break
            elif command == "list":
                self.list_algorithms()
            elif command == "current":
                self.current_algorithm()
            elif command == "switch" and len(parts) > 1:
                self.switch_algorithm(" ".join(parts[1:]))
            elif command == "photo":
                res = parts[1] if len(parts) > 1 else "1280x720"
                fname = self.take_photo(res)
                if fname:
                    self.download_photo(fname)
            elif command == "screenshot":
                self.take_screenshot()
            elif command == "recognize":
                algo = int(parts[1]) if len(parts) > 1 else 0
                self.recognize(algo)
            elif command == "download" and len(parts) > 1:
                self.download_photo(parts[1])
            else:
                print("Unknown command. Use: list, current, switch <name>, photo [res], screenshot, recognize [id], download <file>, quit")


def main():
    parser = argparse.ArgumentParser(description="HUSKYLENS 2 MCP Client")
    parser.add_argument("--host", default="192.168.88.1", help="HUSKYLENS 2 IP address")
    parser.add_argument("--port", type=int, default=3000, help="MCP service port")
    parser.add_argument("command", nargs="?", default="interactive")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()

    client = HuskyLensMCPClient(args.host, args.port)

    try:
        client.connect()
    except ConnectionError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    cmd = args.command.lower()
    try:
        if cmd == "list-algorithms":
            client.list_algorithms()
        elif cmd == "current-algorithm":
            client.current_algorithm()
        elif cmd == "switch-algorithm" and args.args:
            client.switch_algorithm(" ".join(args.args))
        elif cmd == "take-photo":
            res = args.args[0] if args.args else "1280x720"
            fname = client.take_photo(res)
            if fname:
                client.download_photo(fname)
        elif cmd == "screenshot":
            client.take_screenshot()
        elif cmd == "recognize":
            algo = int(args.args[0]) if args.args else 0
            client.recognize(algo)
        elif cmd == "interactive":
            client.interactive()
        else:
            parser.print_help()
    finally:
        client.close()


if __name__ == "__main__":
    main()
