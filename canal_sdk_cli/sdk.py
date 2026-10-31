#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — SDK PYTHON OFFICIEL DU LANCEUR DE CYCLE DE VIE DEV
========================================================================================
Façade unifiée pour intégrer le contrôle de cycle de vie, l'auto-détection polyglotte
multi-OS et le catalogue des 7 Routes dans les scripts, tests et MCP.
========================================================================================
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

_TOOL_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from core.infrastructure.process_supervisor import MultiOsProcessSupervisor
from core.infrastructure.health_probes import HttpHealthProbeAdapter
from core.infrastructure.error_collector import ErrorCollectorAdapter
from core.infrastructure.runtime_state import JsonRuntimeStateAdapter
from core.infrastructure.stack_detector import PolyglotStackDetectorAdapter
from core.application.use_cases import (
    StartDevServicesUseCase,
    StopDevServicesUseCase,
    AuditHealthUseCase,
    GetErrorDiagnosticUseCase,
    DetectProjectStackAndRoutesUseCase,
)


class DevLifecycleLauncherSDK:
    """Façade principale pour orchestrer BatiHome ou tout projet polyglotte en dev."""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = str(Path(project_root).resolve()) if project_root else str(_PROJECT_ROOT)
        self.supervisor = MultiOsProcessSupervisor()
        self.health_probe = HttpHealthProbeAdapter()
        self.error_collector = ErrorCollectorAdapter(_TOOL_ROOT / "output")
        self.state_mgr = JsonRuntimeStateAdapter(_TOOL_ROOT / "state")
        self.stack_detector = PolyglotStackDetectorAdapter()

        self.start_uc = StartDevServicesUseCase(
            supervisor=self.supervisor,
            health_probe=self.health_probe,
            error_collector=self.error_collector,
            state_mgr=self.state_mgr,
            stack_detector=self.stack_detector,
        )
        self.stop_uc = StopDevServicesUseCase(
            supervisor=self.supervisor,
            state_mgr=self.state_mgr,
        )
        self.audit_uc = AuditHealthUseCase(
            supervisor=self.supervisor,
            health_probe=self.health_probe,
        )
        self.diag_uc = GetErrorDiagnosticUseCase(
            error_collector=self.error_collector,
        )
        self.detect_uc = DetectProjectStackAndRoutesUseCase(
            stack_detector=self.stack_detector,
        )

    def detect_stack_and_routes(self, auto_install_deps: bool = False) -> Dict[str, Any]:
        return self.detect_uc.execute(project_root=self.project_root, auto_install_deps=auto_install_deps)

    def start_services(
        self,
        open_browser: bool = True,
        auto_clean: bool = True,
        max_wait_sec: float = 15.0,
        target_route: str = "real",
        auto_install_deps: bool = True,
    ) -> Dict[str, Any]:
        return self.start_uc.execute(
            project_root=self.project_root,
            open_browser=open_browser,
            auto_clean_ports=auto_clean,
            max_wait_sec=max_wait_sec,
            target_route=target_route,
            auto_install_deps=auto_install_deps,
        )

    def stop_services(self, ports: Optional[List[int]] = None) -> Dict[str, Any]:
        return self.stop_uc.execute(ports=ports)

    def audit_health(self) -> Dict[str, Any]:
        return self.audit_uc.execute()

    def get_last_error_diagnostic(self) -> Optional[Dict[str, Any]]:
        return self.diag_uc.execute()

    def start_tunnel(self, port: int = 8000, verify_token: Optional[str] = None) -> Dict[str, Any]:
        """Détecte cloudflared et prépare le tunnel HTTPS public pour l'API et WhatsApp."""
        import shutil

        cloudflared_paths = [
            r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
            r"C:\Program Files\cloudflared\cloudflared.exe",
            shutil.which("cloudflared")
        ]
        exe = next((p for p in cloudflared_paths if p and Path(p).exists()), None)
        if not exe:
            return {
                "status": "UNAVAILABLE",
                "message": "cloudflared non installé. Installation via: winget install --id Cloudflare.cloudflared"
            }

        token = verify_token or "batihome_meta_verify_2026_snorbik"
        return {
            "status": "READY",
            "cloudflared_executable": str(exe),
            "target_port": port,
            "verify_token": token,
            "webhook_path": "/api/v1/whatsapp",
            "command": f'"{exe}" tunnel --url http://127.0.0.1:{port}'
        }
