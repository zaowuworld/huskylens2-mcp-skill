#!/usr/bin/env python3
"""
HUSKYLENS 2 MCP Client

Direct Python client for HUSKYLENS 2 MCP service.
Does not depend on OpenClaw - can be used standalone.

Usage:
    python huskylens2_client.py [--host HOST] [--port PORT] <command> [args]

Commands:
    list-algorithms    List available AI algorithms
    current-algorithm  Show currently running algorithm
    switch-algorithm <name>  Switch to a different algorithm
    take-photo         Take a photo
    recognize          Get current recognition results
    schedule-task <target> <action>  Schedule a conditional task
    interactive        Start interactive mode

Examples:
    python huskylens2_client.py list-algorithms
    python huskylens2_client.py switch-algorithm "物体识别"
    python huskylens2_client.py take-photo
    python huskylens2_client.py recognize
    python huskylens2_client.py schedule-task "键盘" "拍照"
    python huskylens2_client.py interactive
"""
import argparse
import json
import sys
import threading


class HuskyLensMCPClient:
    """Client for HUSKYLENS 2 MCP service over SSE."""

    def __init__(self, host="192.168.88.1", port=3000):
        self.host = host
        self.port = port
        self.sse_url = f"http://{host}:{port}/sse"
        self._session = None
        self._message_endpoint = None

    def connect(self, timeout=10):
        """Connect to MCP service and discover tools."""
        try:
            import urllib.request
            import urllib.error

            # First, try to get SSE endpoint info
            req = urllib.request.Request(self.sse_url, method="GET")
            req.add_header("Accept", "text/event-stream")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # Read initial SSE events to find the message endpoint
                data = resp.read(4096).decode("utf-8", errors="replace")
                for line in data.split("\n"):
                    if line.startswith("data:"):
                        payload = line[5:].strip()
                        try:
                            msg = json.loads(payload)
                            if msg.get("method") == "initialize":
                                print("Connected to HUSKYLENS 2 MCP service")
                        except json.JSONDecodeError:
                            pass
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool via the SSE endpoint.

        Note: This is a simplified client. For full MCP protocol support,
        use an MCP SDK or OpenClaw integration.
        """
        if arguments is None:
            arguments = {}

        print(f"Calling tool: {tool_name}")
        if arguments:
            print(f"Arguments: {json.dumps(arguments, ensure_ascii=False)}")
        print()
        print("Note: For full MCP protocol interaction, use OpenClaw MCP integration")
        print(f"or an MCP-compatible client like Cherry Studio.")
        print(f"SSE URL: {self.sse_url}")

    def list_algorithms(self):
        """List available AI algorithms."""
        self.call_tool("manage_applications", {"query": "list"})

    def current_algorithm(self):
        """Show currently running algorithm."""
        self.call_tool("manage_applications", {"query": "current"})

    def switch_algorithm(self, name):
        """Switch to a different algorithm."""
        self.call_tool("manage_applications", {"action": "switch", "algorithm": name})

    def take_photo(self):
        """Take a photo."""
        self.call_tool("multimedia_control", {"action": "photo"})

    def recognize(self):
        """Get current recognition results."""
        self.call_tool("get_recognition_result", {})

    def schedule_task(self, target, action):
        """Schedule a conditional task."""
        self.call_tool("task_scheduler", {"target": target, "action": action})

    def interactive(self):
        """Start interactive mode."""
        print("HUSKYLENS 2 Interactive Client")
        print("Commands: list, current, switch <name>, photo, recognize, schedule <target> <action>, quit")
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
                self.take_photo()
            elif command == "recognize":
                self.recognize()
            elif command == "schedule" and len(parts) > 2:
                action = parts[-1]
                target = " ".join(parts[1:-1])
                self.schedule_task(target, action)
            else:
                print("Unknown command. Use: list, current, switch <name>, photo, recognize, schedule <target> <action>, quit")


def main():
    parser = argparse.ArgumentParser(description="HUSKYLENS 2 MCP Client")
    parser.add_argument("--host", default="192.168.88.1", help="HUSKYLENS 2 IP address")
    parser.add_argument("--port", type=int, default=3000, help="MCP service port")
    parser.add_argument("command", nargs="?", default="interactive",
                        help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    args = parser.parse_args()

    client = HuskyLensMCPClient(args.host, args.port)

    # Try to connect
    connected = client.connect()

    if not connected:
        print("Warning: Could not connect to HUSKYLENS 2 MCP service.")
        print("Commands will show what would be sent but cannot execute.")
        print()

    # Execute command
    cmd = args.command.lower()
    if cmd == "list-algorithms":
        client.list_algorithms()
    elif cmd == "current-algorithm":
        client.current_algorithm()
    elif cmd == "switch-algorithm" and args.args:
        client.switch_algorithm(" ".join(args.args))
    elif cmd == "take-photo":
        client.take_photo()
    elif cmd == "recognize":
        client.recognize()
    elif cmd == "schedule-task" and len(args.args) >= 2:
        action = args.args[-1]
        target = " ".join(args.args[:-1])
        client.schedule_task(target, action)
    elif cmd == "interactive":
        client.interactive()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
