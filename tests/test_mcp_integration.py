"""
Test d'Intégration Stdio Canonique Universel (JSON-RPC 2.0 / MCP v21.0)
Vérifie : initialize (protocolVersion 2024-11-05), absorption notifications, ping, tools/list.
"""
import sys
import json
import subprocess
from pathlib import Path

def test_stdio_mcp_handshake():
    root = Path(__file__).resolve().parents[1]
    server_file = root / "canal_mcp/mcp_classic_stdio/mcp_server.py"
    assert server_file.exists(), f"Entrypoint introuvable : {server_file}"

    proc = subprocess.Popen(
        [sys.executable, str(server_file)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    # 1. Initialize
    req_init = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-runner", "version": "1.0"}
        }
    }) + "\n"
    proc.stdin.write(req_init)
    proc.stdin.flush()

    line = proc.stdout.readline()
    assert line, "Le serveur n'a renvoyé aucune réponse à initialize"
    resp_init = json.loads(line)
    assert resp_init.get("id") == 1
    assert "protocolVersion" in resp_init.get("result", {})
    assert resp_init["result"]["protocolVersion"] == "2024-11-05"

    # 2. Notification initialized (PAS de réponse attendue)
    req_notif = json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }) + "\n"
    proc.stdin.write(req_notif)
    proc.stdin.flush()

    # 3. Ping
    req_ping = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "ping"
    }) + "\n"
    proc.stdin.write(req_ping)
    proc.stdin.flush()

    line_ping = proc.stdout.readline()
    resp_ping = json.loads(line_ping)
    assert resp_ping.get("id") == 2

    # 4. Tools/list
    req_tools = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/list"
    }) + "\n"
    proc.stdin.write(req_tools)
    proc.stdin.flush()

    line_tools = proc.stdout.readline()
    resp_tools = json.loads(line_tools)
    assert resp_tools.get("id") == 3
    assert "tools" in resp_tools.get("result", {})
    assert len(resp_tools["result"]["tools"]) > 0

    proc.terminate()
    proc.wait(timeout=2)
