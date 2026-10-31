#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — CLI UNIFIÉ (LIGNE DE COMMANDE MULTI-OS & MULTI-ROUTES)
========================================================================================
Permet d'exécuter start, stop, status, detect, routes et diagnose depuis le terminal.
========================================================================================
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from canal_sdk_cli.sdk import DevLifecycleLauncherSDK


def main():
    parser = argparse.ArgumentParser(description="BatiHome Universal Dev Lifecycle Launcher (Outil #09 V2.0)")
    subparsers = parser.add_subparsers(dest="action", help="Action à exécuter")

    # Start
    start_parser = subparsers.add_parser("start", help="Démarre les services (FastAPI 8000 + Vite 3000) et vérifie les 7 routes")
    start_parser.add_argument("--no-browser", action="store_true", help="Ne pas ouvrir le navigateur")
    start_parser.add_argument("--no-clean", action="store_true", help="Ne pas nettoyer les ports au préalable")
    start_parser.add_argument("--timeout", type=float, default=15.0, help="Délai max d'attente (secondes)")
    start_parser.add_argument(
        "--route",
        type=str,
        default="real",
        choices=["real", "configurator", "dev", "console", "backend", "mcp", "api_docs", "database"],
        help="Route cible à ouvrir (real, configurator, dev, console, backend, mcp, api_docs, database)",
    )

    # Stop
    subparsers.add_parser("stop", help="Arrête proprement les services et libère les ports 3000 et 8000")

    # Status / Health
    subparsers.add_parser("status", help="Vérifie la santé des services et sonde les 7 Routes Officielles")

    # Detect (Auto-détection polyglotte OS / Stack / Dépendances)
    detect_parser = subparsers.add_parser("detect", help="Auto-détecte l'OS, les frameworks, les dépendances et les routes")
    detect_parser.add_argument("--install-deps", action="store_true", help="Installer automatiquement les dépendances manquantes")

    # Routes (Liste les 3 routes Front et 4 routes Back)
    subparsers.add_parser("routes", help="Affiche le catalogue complet des 7 Routes Officielles (3 Front + 4 Back)")

    # Diagnose
    subparsers.add_parser("diagnose", help="Affiche le dernier rapport d'erreur structuré pour l'IA")

    args = parser.parse_args()
    sdk = DevLifecycleLauncherSDK()

    if args.action == "start":
        print("🚀 [Launcher #09 V2.0] Auto-détection, vérification des dépendances et démarrage des services...")
        res = sdk.start_services(
            open_browser=not args.no_browser,
            auto_clean=not args.no_clean,
            max_wait_sec=args.timeout,
            target_route=args.route,
        )
        if res.get("success"):
            print("✅ Tous les services sont opérationnels (HEALTHY) !")
            print("\n🌐 LES 3 ROUTES FRONTEND (Port 3000) :")
            print("   1. Projet Réel & 6 Étapes : http://localhost:3000/#P01_home  |  http://localhost:3000/#P04_configurateur")
            print("   2. Projet Dev Workbench   : http://localhost:3000/#dev")
            print("   3. Console Pilote IA V9   : http://localhost:3000/#console")
            print("\n⚙️  LES 4 ROUTES BACKEND & MCP (Port 8000) :")
            print("   1. Portail Backend & Santé: http://127.0.0.1:8000/  |  http://127.0.0.1:8000/api/v1/health")
            print("   2. Hub MCP (9 Outils MCP) : http://127.0.0.1:8000/api/v1/mcp/registry")
            print("   3. API Doc Swagger/ReDoc  : http://127.0.0.1:8000/docs  |  http://127.0.0.1:8000/redoc")
            print("   4. Database SQLite WAL    : http://127.0.0.1:8000/api/v1/database")
            sys.exit(0)
        else:
            print("❌ Défaillance lors du démarrage des services.")
            diag = res.get("diagnostic")
            if diag:
                print("\n📋 Fiche de Diagnostic d'Erreur :")
                print(f"   Cause racine : {diag.get('root_cause_hint')}")
                print(f"   Remède       : {diag.get('actionable_remedy')}")
            sys.exit(1)

    elif args.action == "stop":
        print("🛑 [Launcher #09] Arrêt des services et libération des ports 3000 & 8000...")
        res = sdk.stop_services()
        print(f"✅ Services arrêtés. Ports libérés : {res.get('freed_ports')}")
        sys.exit(0)

    elif args.action == "status":
        res = sdk.audit_health()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("overall_status") == "HEALTHY" else 1)

    elif args.action == "detect":
        res = sdk.detect_stack_and_routes(auto_install_deps=args.install_deps)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    elif args.action == "routes":
        res = sdk.detect_stack_and_routes(auto_install_deps=False)
        print(json.dumps({"routes_catalog": res["routes_catalog"], "shortcuts": res["route_shortcuts"]}, indent=2, ensure_ascii=False))
        sys.exit(0)

    elif args.action == "diagnose":
        diag = sdk.get_last_error_diagnostic()
        if diag:
            print(json.dumps(diag, indent=2, ensure_ascii=False))
            sys.exit(0)
        else:
            print("Aucune anomalie récente enregistrée.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
