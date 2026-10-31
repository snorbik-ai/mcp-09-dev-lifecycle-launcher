"""
Test de Validation Structurelle de l'Installateur Multi-Clients (v22.1)
Vérifie la conformité exacte des schémas JSON pour chaque client supporté :
1. VS Code (.vscode/mcp.json) : clé obligatoire "servers" (spécification officielle).
2. Cursor (~/.cursor/mcp.json) : clé "mcpServers".
3. Claude Desktop (claude_desktop_config.json) : clé "mcpServers".
"""
import json
import tempfile
from pathlib import Path
import sys

_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

import install

def test_vscode_servers_key_compliance():
    """Valide que la configuration VS Code utilise bien la clé officielle 'servers'."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        entry = {"command": "python", "args": ["main.py"]}
        
        ok = install.configure_vscode(entry, target_root=tmp_path)
        assert ok is True
        
        cfg_file = tmp_path / ".vscode" / "mcp.json"
        assert cfg_file.exists(), "Le fichier .vscode/mcp.json n'a pas été créé"
        
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
        assert "servers" in data, "Violation de spécification : la clé racine DOIT être 'servers' pour VS Code"
        assert "mcpServers" not in data, "La clé 'mcpServers' ne doit pas être utilisée dans .vscode/mcp.json"
        assert install.COMPONENT_NAME in data["servers"]
        assert data["servers"][install.COMPONENT_NAME]["command"] == "python"

def test_cursor_mcpservers_key_compliance():
    """Valide que la configuration Cursor utilise bien la clé 'mcpServers'."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        entry = {"command": "python", "args": ["main.py"], "type": "stdio"}
        
        ok = install.configure_cursor(entry, custom_home=tmp_path)
        assert ok is True
        
        cfg_file = tmp_path / ".cursor" / "mcp.json"
        assert cfg_file.exists(), "Le fichier .cursor/mcp.json n'a pas été créé"
        
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
        assert "mcpServers" in data
        assert install.COMPONENT_NAME in data["mcpServers"]

def test_claude_desktop_key_compliance():
    """Valide que la configuration Claude Desktop utilise bien la clé 'mcpServers'."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        claude_dir = tmp_path / "Claude"
        claude_dir.mkdir(parents=True)
        entry = {"command": "python", "args": ["main.py"]}
        
        ok = install.configure_claude_desktop(entry, custom_appdata=tmp_path)
        assert ok is True
        
        cfg_file = claude_dir / "claude_desktop_config.json"
        assert cfg_file.exists()
        
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
        assert "mcpServers" in data
        assert install.COMPONENT_NAME in data["mcpServers"]
