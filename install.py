#!/usr/bin/env python3
"""
Script d'Installation 1-Clic Autonome & Injection Cursor MCP — mcp-09-dev-lifecycle-launcher
Snorbik AI Architecture V14.1
"""
import sys
import os
import json
import subprocess
from pathlib import Path

MIN_PYTHON = (3, 10)
COMPONENT_NAME = "mcp-09-dev-lifecycle-launcher"
IS_NODE = False
IS_SDK = False
ENTRYPOINT_REL = "canal_mcp/mcp_classic_stdio/mcp_server.py"

def check_python_version():
    if sys.version_info < MIN_PYTHON:
        print(f"[-] Erreur : Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ requis. Version actuelle : {sys.version}")
        sys.exit(1)
    print(f"[+] Python {sys.version.split()[0]} détecté (OK).")

def install_dependencies(root_dir: Path):
    print(f"[*] Installation des dépendances pour {COMPONENT_NAME}...")
    if IS_NODE:
        if (root_dir / "package.json").exists():
            res = subprocess.run(["npm", "install"], cwd=str(root_dir), shell=True)
            if res.returncode == 0:
                print("[+] Dépendances Node.js installées avec succès.")
            else:
                print("[-] Attention : échec lors de npm install.")
    else:
        # Python
        if (root_dir / "pyproject.toml").exists() or (root_dir / "setup.py").exists():
            res = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=str(root_dir), shell=True)
            if res.returncode == 0:
                print("[+] Package installé en mode éditable (pip install -e .).")
            else:
                print("[-] Attention : échec lors de pip install -e .")
        elif (root_dir / "requirements.txt").exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(root_dir), shell=True)
            print("[+] Dépendances requirements.txt installées.")

def configure_cursor_mcp(root_dir: Path):
    if IS_SDK:
        print("[i] Composant de type SDK : pas de configuration serveur STDIO nécessaire dans Cursor.")
        return True

    cursor_dir = Path.home() / ".cursor"
    cursor_config = cursor_dir / "mcp.json"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    
    config_data = {"mcpServers": {}}
    if cursor_config.exists():
        try:
            with open(cursor_config, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    config_data = json.loads(content)
                if "mcpServers" not in config_data:
                    config_data["mcpServers"] = {}
        except Exception as e:
            print(f"[!] Avertissement lecture cursor mcp.json (création nouveau format) : {e}")
            config_data = {"mcpServers": {}}

    entrypoint_full = (root_dir / ENTRYPOINT_REL).resolve()
    
    if IS_NODE:
        server_entry = {
            "command": "node",
            "args": [str(entrypoint_full.as_posix())],
            "type": "stdio"
        }
    else:
        server_entry = {
            "command": sys.executable if sys.executable else "python",
            "args": [str(entrypoint_full.as_posix())],
            "env": {
                "PYTHONIOENCODING": "utf-8"
            },
            "type": "stdio"
        }
    
    config_data["mcpServers"][COMPONENT_NAME] = server_entry
    
    with open(cursor_config, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print(f"[+] Configuration injectée avec succès dans {cursor_config}.")
    print(f"    -> Entrée '{COMPONENT_NAME}' configurée avec cible : {entrypoint_full}")
    return True

def main():
    print("=" * 70)
    print(f"INSTALLATION 1-CLIC : {COMPONENT_NAME}")
    print("=" * 70)
    
    root_dir = Path(__file__).resolve().parent
    check_python_version()
    install_dependencies(root_dir)
    configure_cursor_mcp(root_dir)
    
    print("=" * 70)
    print(f"✅ Serveur MCP {COMPONENT_NAME} installé et configuré dans Cursor avec succès !")
    print("=" * 70)

if __name__ == "__main__":
    main()
