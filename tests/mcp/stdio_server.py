import json
import sys


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    request = json.loads(line)

    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "test-mcp-server",
                        "version": "1.0.0",
                    },
                },
            }
        )

    elif method == "notifications/initialized":
        continue

    elif method == "tools/list":
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "add",
                            "description": "Add two integers",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "a": {
                                        "type": "integer"
                                    },
                                    "b": {
                                        "type": "integer"
                                    },
                                },
                                "required": ["a", "b"],
                            },
                        }
                    ]
                },
            }
        )

    elif method == "tools/call":
        arguments = request["params"]["arguments"]

        total = (
            arguments["a"] +
            arguments["b"]
        )

        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(total),
                        }
                    ]
                },
            }
        )