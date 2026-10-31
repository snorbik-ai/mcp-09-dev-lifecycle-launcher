#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — PORTE A : SERVEUR MCP STDIO OFFICIEL (JSON-RPC 2.0)
========================================================================================
Permet aux IDEs et agents d'IA (Cursor, Antigravity, Claude Code, Windsurf) de piloter
le cycle de vie du projet BatiHome (FastAPI 8000 + Vite 3000) et d'obtenir en direct
les rapports de santé et fiches de diagnostic d'erreur.
========================================================================================
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

_CURRENT_DIR = Path(__file__).resolve().parent
_TOOL_ROOT = _CURRENT_DIR.parents[1]
_PROJECT_ROOT = _TOOL_ROOT.parent.parent

if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from canal_sdk_cli.sdk import DevLifecycleLauncherSDK

sdk = DevLifecycleLauncherSDK(project_root=str(_PROJECT_ROOT))
CONTEXT_FILE = _TOOL_ROOT / "canal_mcp" / "mcp_agent_coding" / "context_llm.json"


def _load_context() -> Dict[str, Any]:
    if not CONTEXT_FILE.exists():
        return {}
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


TOOLS_METADATA = [
    {
        "name": "run_agent_lifecycle",
        "description": (
            "POINT D'ENTRÉE UNIQUE ET OBLIGATOIRE du Superviseur de Cycle de Vie Dev Polyglotte Multi-OS (Outil #09 V2.0).\n"
            "Permet à l'IA d'auto-détecter l'OS (Windows/Linux/macOS), les frameworks (FastAPI, Django, Vite, Express, Go, Rust), "
            "vérifier/installer les dépendances, démarrer les services, sonder les 7 Routes Officielles (3 Front + 4 Back/MCP/DB) "
            "ou récupérer le diagnostic d'erreur.\n"
            "Actions disponibles : 'start_services', 'stop_services', 'audit_health', 'detect_stack_and_routes', 'get_error_diagnostic'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "start_services",
                        "stop_services",
                        "audit_health",
                        "detect_stack_and_routes",
                        "get_error_diagnostic",
                    ],
                    "description": "Action de cycle de vie à exécuter."
                },
                "target_route": {
                    "type": "string",
                    "enum": ["real", "configurator", "dev", "console", "backend", "mcp", "api_docs", "database"],
                    "description": "Route parmi les 7 routes officielles à ouvrir/cibler (défaut 'real').",
                    "default": "real"
                },
                "auto_install_deps": {
                    "type": "boolean",
                    "description": "Vérifier et installer automatiquement les dépendances manquantes.",
                    "default": True
                },
                "open_browser": {
                    "type": "boolean",
                    "description": "Ouvrir le navigateur web (défaut False pour un agent IA).",
                    "default": False
                },
                "auto_clean_ports": {
                    "type": "boolean",
                    "description": "Libérer préventivement les ports 3000/8000 en cas de conflit.",
                    "default": True
                },
                "timeout_sec": {
                    "type": "number",
                    "description": "Délai max d'attente des sondes HTTP en secondes (défaut 15.0).",
                    "default": 15.0
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "dev_start_services",
        "description": "Démarre l'API FastAPI (8000) et le frontend Vite (3000) en mode dev avec sondes de santé.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "open_browser": {"type": "boolean", "default": False},
                "auto_clean": {"type": "boolean", "default": True}
            }
        }
    },
    {
        "name": "dev_stop_services",
        "description": "Arrête tous les services actifs BatiHome et libère les ports 3000 et 8000.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "dev_audit_health",
        "description": "Vérifie l'état des ports et la réponse HTTP des sondes de santé.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "dev_get_error_diagnostic",
        "description": "Récupère la fiche d'erreur structurée (cause racine, remède suggéré et traceback) pour que l'IA corrige le bug.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "dev_start_tunnel",
        "description": "Prépare ou lance le tunnel Cloudflare HTTPS vers l'API FastAPI locale pour tester les webhooks Meta WhatsApp en direct.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "port": {"type": "integer", "description": "Port local à exposer (défaut 8000).", "default": 8000},
                "verify_token": {"type": "string", "description": "Jeton de vérification Meta optionnel."}
            }
        }
    }
]


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "run_agent_lifecycle":
        action = arguments.get("action", "audit_health")
        if action == "start_services":
            return sdk.start_services(
                open_browser=arguments.get("open_browser", False),
                auto_clean=arguments.get("auto_clean_ports", True),
                max_wait_sec=arguments.get("timeout_sec", 15.0),
                target_route=arguments.get("target_route", "real"),
                auto_install_deps=arguments.get("auto_install_deps", True),
            )
        elif action == "stop_services":
            return sdk.stop_services()
        elif action == "audit_health":
            return sdk.audit_health()
        elif action == "detect_stack_and_routes":
            return sdk.detect_stack_and_routes(
                auto_install_deps=arguments.get("auto_install_deps", False)
            )
        elif action == "get_error_diagnostic":
            diag = sdk.get_last_error_diagnostic()
            return diag or {"message": "Aucune erreur récente enregistrée."}
        else:
            raise ValueError(f"Action inconnue : {action}")

    elif tool_name == "dev_start_services":
        return sdk.start_services(
            open_browser=arguments.get("open_browser", False),
            auto_clean=arguments.get("auto_clean", True)
        )

    elif tool_name == "dev_stop_services":
        return sdk.stop_services()

    elif tool_name == "dev_audit_health":
        return sdk.audit_health()

    elif tool_name == "dev_get_error_diagnostic":
        diag = sdk.get_last_error_diagnostic()
        return diag or {"message": "Aucune erreur récente enregistrée."}

    elif tool_name == "dev_start_tunnel":
        port = int(arguments.get("port", 8000))
        token = arguments.get("verify_token")
        return sdk.start_tunnel(port=port, verify_token=token)

    else:
        raise ValueError(f"Outil MCP inconnu: {tool_name}")


def run_stdio_server():
    """Boucle principale JSON-RPC 2.0 sur stdin / stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "09-dev-lifecycle-launcher",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        }
                    }
                }

            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_METADATA}}

            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                result = handle_tool_call(name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
                    }
                }

            elif method == "resources/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "resources": [
                            {
                                "uri": "context://plan/context_llm.json",
                                "name": "Plan Directeur & GPS Cycle de Vie Dev",
                                "mimeType": "application/json"
                            }
                        ]
                    }
                }

            elif method == "resources/read":
                params = req.get("params", {})
                uri = params.get("uri")
                if uri == "context://plan/context_llm.json":
                    content = _load_context()
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": json.dumps(content, indent=2, ensure_ascii=False)
                                }
                            ]
                        }
                    }
                else:
                    resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Resource not found"}}

            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
