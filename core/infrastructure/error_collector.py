#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — COLLECTEUR D'ERREURS & SYNTHÈSE DIAGNOSTIC IA (LLM-READY)
========================================================================================
Isole les causes racines dans les logs bruts des sous-processus et produit des fiches
de remédiation synthétiques destinées aux modèles de langage (LLM / Agent).
========================================================================================
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

from ..domain.entities_and_ports import IErrorCollectorPort, ErrorDiagnosticDigest


class ErrorCollectorAdapter(IErrorCollectorPort):
    """Adaptateur de collecte et de diagnostic d'erreurs pour l'IA."""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            self.output_dir = Path(__file__).resolve().parents[2] / "output"
        else:
            self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.diagnostic_file = self.output_dir / "last_error_diagnostic.json"

    def capture_error(
        self,
        service_id: str,
        command: str,
        stderr_lines: List[str],
        exit_code: Optional[int] = None
    ) -> ErrorDiagnosticDigest:
        raw_text = "\n".join(stderr_lines)
        error_type, root_cause, remedy, clean_tb = self._analyze_error(raw_text, service_id)

        digest = ErrorDiagnosticDigest(
            timestamp=time.time(),
            service_id=service_id,
            error_type=error_type,
            command=command,
            exit_code=exit_code,
            raw_stderr=raw_text[:2000],  # Tronquer pour préserver la fenêtre de contexte
            clean_traceback=clean_tb,
            root_cause_hint=root_cause,
            actionable_remedy=remedy
        )

        self.save_last_diagnostic(digest)
        return digest

    def _analyze_error(self, raw_text: str, service_id: str):
        """Détecte les motifs d'erreurs connus et produit le conseil de remédiation."""
        # 1. Port déjà occupé (EADDRINUSE / WinError 10048)
        if "EADDRINUSE" in raw_text or "address already in use" in raw_text.lower() or "winerror 10048" in raw_text.lower():
            match_port = (
                re.search(r":::(\d+)", raw_text)
                or re.search(r"port\s*[:=]?\s*(\d+)", raw_text, re.IGNORECASE)
                or re.search(r":(\d{4,5})\b", raw_text)
            )
            port_str = match_port.group(1) if match_port else "3000/8000"
            return (
                "PORT_CONFLICT_EADDRINUSE",
                f"Le port {port_str} est déjà verrouillé par un processus existant.",
                f"Exécutez 'python -m outils_internes.09_dev_lifecycle_launcher.canal_sdk_cli.cli stop' ou libérez le port {port_str}.",
                raw_text[-300:]
            )

        # 2. Module Python manquant
        match_module = re.search(r"ModuleNotFoundError:\s+No module named\s+'([^']+)'", raw_text)
        if match_module:
            pkg = match_module.group(1)
            return (
                "PYTHON_MODULE_NOT_FOUND",
                f"Dépendance Python manquante : module '{pkg}'.",
                f"Exécutez 'pip install {pkg}' ou vérifiez l'environnement virtuel actif.",
                match_module.group(0)
            )

        # 3. Erreur de syntaxe Python
        if "SyntaxError:" in raw_text:
            lines = [l for l in raw_text.splitlines() if "SyntaxError:" in l or "File " in l]
            return (
                "PYTHON_SYNTAX_ERROR",
                "Erreur de syntaxe détectée dans le code source Python.",
                "Inspectez et corrigez le fichier indiqué dans la traceback.",
                "\n".join(lines[-4:])
            )

        # 4. Erreur TypeScript / Vite
        if "Failed to resolve import" in raw_text or "Could not resolve" in raw_text:
            return (
                "FRONTEND_IMPORT_RESOLUTION_ERROR",
                "Le frontend Vite ne parvient pas à importer un module ou un fichier.",
                "Vérifiez les chemins d'importation relatifs et le fichier package.json dans frontend/.",
                raw_text[-400:]
            )

        # 5. Base de données SQLite verrouillée ou table manquante
        if "sqlite3.OperationalError" in raw_text or "no such table" in raw_text:
            return (
                "SQLITE_DATABASE_ERROR",
                "Anomalie de schéma ou verrouillage de base de données SQLite.",
                "Vérifiez l'initialisation du schéma dans backend/infrastructure/persistence/sqlite/.",
                raw_text[-300:]
            )

        # Fallback générique
        return (
            "UNCLASSIFIED_RUNTIME_ERROR",
            f"Défaillance d'exécution non répertoriée sur le service {service_id}.",
            "Consultez les dernières lignes de stderr dans last_error_diagnostic.json pour corriger le composant.",
            raw_text[-400:] if raw_text else "Stderr vide."
        )

    def save_last_diagnostic(self, digest: ErrorDiagnosticDigest) -> str:
        with open(self.diagnostic_file, "w", encoding="utf-8") as f:
            json.dump(digest.to_dict(), f, indent=2, ensure_ascii=False)
        return str(self.diagnostic_file)

    def get_last_diagnostic(self) -> Optional[ErrorDiagnosticDigest]:
        if not self.diagnostic_file.exists():
            return None
        try:
            with open(self.diagnostic_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ErrorDiagnosticDigest(**data)
        except Exception:
            return None
