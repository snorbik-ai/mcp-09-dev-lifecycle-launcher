#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — USE CASES D'ORCHESTRATION DU CYCLE DE VIE DEV (CLEAN ARCHITECTURE)
========================================================================================
Assemble les ports de domaine pour exécuter l'auto-détection polyglotte multi-OS,
la vérification des dépendances, le démarrage, l'arrêt, la surveillance des 7 Routes
et le diagnostic d'erreurs en mode développement.
========================================================================================
"""
from __future__ import annotations

import os
import sys
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..domain.entities_and_ports import (
    IProcessSupervisorPort,
    IHealthProbePort,
    IErrorCollectorPort,
    IRuntimeStatePort,
    IStackDetectorPort,
    ServiceStatus,
    OverallHealthReport,
    ErrorDiagnosticDigest,
    OFFICIAL_PROJECT_ROUTES,
)


ROUTE_SHORTCUTS: Dict[str, str] = {
    "real": "http://localhost:3000/#P01_home",
    "configurator": "http://localhost:3000/#P04_configurateur",
    "dev": "http://localhost:3000/#dev",
    "console": "http://localhost:3000/#console",
    "backend": "http://127.0.0.1:8000/",
    "mcp": "http://127.0.0.1:8000/api/v1/mcp/registry",
    "api_docs": "http://127.0.0.1:8000/docs",
    "database": "http://127.0.0.1:8000/api/v1/database",
}


class DetectProjectStackAndRoutesUseCase:
    """Use case : Auto-détecte l'OS, les langages/frameworks, les dépendances et expose les 7 Routes."""

    def __init__(self, stack_detector: IStackDetectorPort):
        self.stack_detector = stack_detector

    def execute(self, project_root: str, auto_install_deps: bool = False) -> Dict[str, Any]:
        blueprint = self.stack_detector.detect_project_blueprint(project_root)
        deps_report = {}
        if auto_install_deps:
            deps_report = self.stack_detector.verify_and_install_dependencies(blueprint, auto_install=True)
        else:
            deps_report = self.stack_detector.verify_and_install_dependencies(blueprint, auto_install=False)

        res = blueprint.to_dict()
        res["dependencies_audit"] = deps_report
        res["route_shortcuts"] = ROUTE_SHORTCUTS
        return res


class StartDevServicesUseCase:
    """Use case : Auto-détecte, vérifie les dépendances et démarre les services avec sondes sur les 7 Routes."""

    def __init__(
        self,
        supervisor: IProcessSupervisorPort,
        health_probe: IHealthProbePort,
        error_collector: IErrorCollectorPort,
        state_mgr: IRuntimeStatePort,
        stack_detector: Optional[IStackDetectorPort] = None,
    ):
        self.supervisor = supervisor
        self.health_probe = health_probe
        self.error_collector = error_collector
        self.state_mgr = state_mgr
        self.stack_detector = stack_detector

    def execute(
        self,
        project_root: str,
        open_browser: bool = True,
        auto_clean_ports: bool = True,
        max_wait_sec: float = 15.0,
        target_route: str = "real",
        auto_install_deps: bool = True,
    ) -> Dict[str, Any]:
        root_path = Path(project_root).resolve()

        # 1. Étape 1 : Auto-détection polyglotte & vérification des dépendances
        blueprint_dict = None
        deps_audit = None
        if self.stack_detector is not None:
            blueprint = self.stack_detector.detect_project_blueprint(str(root_path))
            deps_audit = self.stack_detector.verify_and_install_dependencies(
                blueprint, auto_install=auto_install_deps
            )
            blueprint_dict = blueprint.to_dict()
            ports = [s.port for s in blueprint.detected_services] or [8000, 3000]
        else:
            ports = [8000, 3000]

        # 2. Étape 2 : Nettoyage préventif des ports si demandé
        freed_pids = []
        if auto_clean_ports:
            freed_pids = self.supervisor.clean_ports(ports)

        # 3. Étape 3 : Commandes de lancement (issues de l'auto-détection ou repli standard)
        is_win = os.name == "nt"
        python_bin = sys.executable
        npm_bin = "npm.cmd" if is_win else "npm"

        backend_cmd = [
            python_bin,
            "-m",
            "uvicorn",
            "backend.entrypoints.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ]
        frontend_cmd = [npm_bin, "--prefix", "frontend", "run", "dev"]

        if self.stack_detector is not None and blueprint.detected_services:
            for svc in blueprint.detected_services:
                if svc.service_id == "backend":
                    backend_cmd = svc.start_command
                elif svc.service_id == "frontend":
                    frontend_cmd = svc.start_command

        # 4. Étape 4 : Lancement supervisé des services
        backend_state = self.supervisor.spawn_service(
            service_id="backend", command=backend_cmd, cwd=str(root_path)
        )
        time.sleep(1.0)

        frontend_state = self.supervisor.spawn_service(
            service_id="frontend", command=frontend_cmd, cwd=str(root_path)
        )

        # Persistance immédiate des PIDs et du catalogue des 7 routes
        runtime_data = {
            "started_at": time.time(),
            "project_root": str(root_path),
            "services": {
                "backend": backend_state.to_dict(),
                "frontend": frontend_state.to_dict(),
            },
            "routes_catalog": OFFICIAL_PROJECT_ROUTES,
        }
        self.state_mgr.save_state(runtime_data)

        # 5. Étape 5 : Sondes de santé principales
        targets = {
            "backend": "http://127.0.0.1:8000/api/v1/health",
            "frontend": "http://localhost:3000/",
        }
        health_report = self.health_probe.poll_until_ready(targets, max_wait_sec=max_wait_sec)
        is_success = health_report.overall_status == "HEALTHY"

        # 6. Diagnostic si échec
        diagnostic = None
        if not is_success:
            from ..infrastructure.process_supervisor import MultiOsProcessSupervisor

            if isinstance(self.supervisor, MultiOsProcessSupervisor):
                b_logs = self.supervisor.get_recent_logs("backend", 40)
                f_logs = self.supervisor.get_recent_logs("frontend", 40)
                all_err_lines = b_logs + f_logs
                diagnostic = self.error_collector.capture_error(
                    service_id="system_trio",
                    command="StartDevServices",
                    stderr_lines=all_err_lines,
                    exit_code=1,
                ).to_dict()

        # 7. Ouverture du navigateur sur la route choisie (parmi les 7 routes)
        opened_url = ROUTE_SHORTCUTS.get(target_route, "http://localhost:3000/#P01_home")
        if is_success and open_browser:
            try:
                webbrowser.open(opened_url)
            except Exception:
                pass

        return {
            "success": is_success,
            "status": "HEALTHY" if is_success else "DEGRADED",
            "opened_route": opened_url,
            "freed_pids": freed_pids,
            "dependencies_audit": deps_audit,
            "blueprint": blueprint_dict,
            "routes": OFFICIAL_PROJECT_ROUTES,
            "route_shortcuts": ROUTE_SHORTCUTS,
            "runtime": runtime_data,
            "health": health_report.to_dict(),
            "diagnostic": diagnostic,
        }


class StopDevServicesUseCase:
    """Use case : Arrêt ordonné des sous-processus et libération garantie des ports."""

    def __init__(self, supervisor: IProcessSupervisorPort, state_mgr: IRuntimeStatePort):
        self.supervisor = supervisor
        self.state_mgr = state_mgr

    def execute(self, ports: Optional[List[int]] = None) -> Dict[str, Any]:
        if ports is None:
            ports = [8000, 3000]

        state = self.state_mgr.load_state()
        stopped_pids = []

        services = state.get("services", {})
        for _s_id, s_data in services.items():
            pid = s_data.get("pid")
            if pid:
                if self.supervisor.stop_service(pid):
                    stopped_pids.append(pid)

        cleaned_pids = self.supervisor.clean_ports(ports)
        all_stopped = list(set(stopped_pids + cleaned_pids))
        self.state_mgr.clear_state()

        return {
            "success": True,
            "status": "STOPPED",
            "stopped_pids": all_stopped,
            "freed_ports": ports,
        }


class AuditHealthUseCase:
    """Use case : Audit instantané de la santé des services, des ports et des 7 Routes Officielles."""

    def __init__(self, supervisor: IProcessSupervisorPort, health_probe: IHealthProbePort):
        self.supervisor = supervisor
        self.health_probe = health_probe

    def execute(self) -> Dict[str, Any]:
        targets = {
            "backend": "http://127.0.0.1:8000/api/v1/health",
            "frontend": "http://localhost:3000/",
        }
        b_check = self.health_probe.check_http_health("backend", targets["backend"], timeout_sec=1.5)
        f_check = self.health_probe.check_http_health("frontend", targets["frontend"], timeout_sec=1.5)

        # Sondes complémentaires sur les routes Backend (MCP Registry, API Docs, Database SQLite)
        mcp_check = self.health_probe.check_http_health(
            "back_2_mcp_registry", "http://127.0.0.1:8000/api/v1/mcp/registry", timeout_sec=1.5
        )
        docs_check = self.health_probe.check_http_health(
            "back_3_api_docs", "http://127.0.0.1:8000/docs", timeout_sec=1.5
        )
        db_check = self.health_probe.check_http_health(
            "back_4_database", "http://127.0.0.1:8000/api/v1/database", timeout_sec=1.5
        )

        open_ports = self.supervisor.get_open_ports([8000, 3000])
        is_healthy = b_check.is_healthy and f_check.is_healthy

        return {
            "overall_status": "HEALTHY" if is_healthy else "DEGRADED",
            "open_ports": open_ports,
            "services": {
                "backend": b_check.to_dict(),
                "frontend": f_check.to_dict(),
            },
            "routes_probes": {
                "back_1_health": b_check.to_dict(),
                "back_2_mcp_registry": mcp_check.to_dict(),
                "back_3_api_docs": docs_check.to_dict(),
                "back_4_database": db_check.to_dict(),
                "front_all_3_routes": f_check.to_dict(),
            },
            "routes_catalog": OFFICIAL_PROJECT_ROUTES,
            "route_shortcuts": ROUTE_SHORTCUTS,
        }


class GetErrorDiagnosticUseCase:
    """Use case : Récupération du dernier diagnostic d'erreur structuré pour l'IA."""

    def __init__(self, error_collector: IErrorCollectorPort):
        self.error_collector = error_collector

    def execute(self) -> Optional[Dict[str, Any]]:
        diag = self.error_collector.get_last_diagnostic()
        return diag.to_dict() if diag else None
