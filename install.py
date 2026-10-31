#!/usr/bin/env python3
"""
Script d'Installation Multi-Clients Universel & Injection MCP (v21.0)
Support : Cursor, VS Code / Copilot, Claude Desktop, Claude Code CLI.
Snorbik AI Architecture V21.0
"""
import sys
from snorbik_bootstrap import get_guaranteed_python
PYTHON_BIN = get_guaranteed_python()
import os
import json
import argparse
import platform
import subprocess
from pathlib import Path

MIN_PYTHON = (3, 10)
COMPONENT_NAME = "mcp-09-dev-lifecycle-launcher"
IS_NODE = False
ENTRYPOINT_REL = "canal_mcp/mcp_classic_stdio/mcp_server.py"

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        sys.stderr.write(f"[-] Erreur : Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ requis. Version actuelle : {sys.version}\n")
        sys.exit(1)
    print(f"[+] Python {sys.version.split()[0]} validé (OK).")

def install_dependencies(root_dir: Path):
    print(f"[*] Installation des dépendances pour {COMPONENT_NAME}...")
    if IS_NODE:
        if (root_dir / "package.json").exists():
            subprocess.run(["npm", "install"], cwd=str(root_dir), shell=True)
    else:
        if (root_dir / "pyproject.toml").exists() or (root_dir / "setup.py").exists():
            subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "-e", "."], cwd=str(root_dir), shell=True, capture_output=True)
        elif (root_dir / "requirements.txt").exists():
            subprocess.run([str(PYTHON_BIN), "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(root_dir), shell=True, capture_output=True)
    print(f"[+] Dépendances opérationnelles.")

def get_server_entry(entrypoint_full: Path) -> dict:
    if IS_NODE:
        return {
            "command": "node",
            "args": [str(entrypoint_full.as_posix())],
            "type": "stdio"
        }
    return {
        "command": str(PYTHON_BIN) if str(PYTHON_BIN) else "python",
        "args": [str(entrypoint_full.as_posix())],
        "env": {"PYTHONIOENCODING": "utf-8"},
        "type": "stdio"
    }

def configure_cursor(server_entry: dict):
    cursor_dir = Path.home() / ".cursor"
    cursor_config = cursor_dir / "mcp.json"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    _inject_config(cursor_config, "mcpServers", COMPONENT_NAME, server_entry, "Cursor")

def configure_vscode(server_entry: dict):
    vscode_dir = Path.cwd() / ".vscode"
    vscode_config = vscode_dir / "mcp.json"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    entry_vscode = {k: v for k, v in server_entry.items() if k != "type"}
    _inject_config(vscode_config, "mcpServers", COMPONENT_NAME, entry_vscode, "VS Code")

def configure_claude_desktop(server_entry: dict):
    system = platform.system()
    if system == "Windows":
        app_data = os.environ.get("APPDATA")
        if not app_data:
            return
        claude_dir = Path(app_data) / "Claude"
    elif system == "Darwin":
        claude_dir = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        claude_dir = Path.home() / ".config" / "Claude"
    
    claude_config = claude_dir / "claude_desktop_config.json"
    entry_claude = {k: v for k, v in server_entry.items() if k != "type"}
    _inject_config(claude_config, "mcpServers", COMPONENT_NAME, entry_claude, "Claude Desktop", create_parents=False)

def _inject_config(file_path: Path, root_key: str, server_name: str, entry: dict, client_name: str, create_parents=True):
    try:
        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        elif not file_path.parent.exists():
            return
        
        data = {root_key: {}}
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8").strip()
                if content:
                    data = json.loads(content)
                if root_key not in data:
                    data[root_key] = {}
            except Exception:
                data = {root_key: {}}
        
        data[root_key][server_name] = entry
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[+] Injecté dans {client_name} : {file_path}")
    except Exception as e:
        sys.stderr.write(f"[-] Avertissement injection {client_name} : {e}\n")

def print_claude_code_command(entrypoint_full: Path):
    cmd_str = f'claude mcp add {COMPONENT_NAME} "{PYTHON_BIN}" "{entrypoint_full.as_posix()}"'
    print(f"[*] Commande Claude Code CLI :\n    {cmd_str}")

def main():
    parser = argparse.ArgumentParser(description=f"Installateur Multi-Clients {COMPONENT_NAME}")
    parser.add_argument("--client", choices=["all", "cursor", "vscode", "claude"], default="all",
                        help="Client cible (défaut : all pour auto-détection)")
    args = parser.parse_args()

    print("=" * 70)
    print(f"INSTALLATEUR MULTI-CLIENTS : {COMPONENT_NAME} (v21.0)")
    print("=" * 70)

    root_dir = Path(__file__).resolve().parent
    check_python_version()
    install_dependencies(root_dir)

    entrypoint_full = (root_dir / ENTRYPOINT_REL).resolve()
    server_entry = get_server_entry(entrypoint_full)

    if args.client in ("all", "cursor"):
        configure_cursor(server_entry)
    if args.client in ("all", "vscode"):
        configure_vscode(server_entry)
    if args.client in ("all", "claude"):
        configure_claude_desktop(server_entry)
        print_claude_code_command(entrypoint_full)

    print("=" * 70)
    print(f"✅ Serveur MCP {COMPONENT_NAME} installé avec succès !")
    print("💡 RAPPEL DX : Rechargez votre IDE ('Developer: Reload Window') pour l'activer.")
    print("=" * 70)

if __name__ == "__main__":
    main()
