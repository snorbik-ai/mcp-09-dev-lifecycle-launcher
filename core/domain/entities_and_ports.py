#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — DOMAIN ENTITIES & PORTS ABSTRAITS (CLEAN ARCHITECTURE)
========================================================================================
Définit les contrats fondamentaux du cycle de vie des services, des rapports de santé
et des digests de diagnostic d'erreur destinés aux agents IA.
========================================================================================
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional
import time


class ServiceType(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"


class ServiceStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRASHED = "CRASHED"


# Catalogue canonique des 7 Routes Officielles (3 Routes Front + 4 Routes Back/MCP/DB)
OFFICIAL_PROJECT_ROUTES: Dict[str, Any] = {
    "frontend_routes": {
        "1_projet_reel": {
            "id": "FRONT_1_REAL",
            "label": "Projet Réel E-Commerce & Configurateur 6 Étapes",
            "url_home": "http://localhost:3000/#P01_home",
            "url_configurator": "http://localhost:3000/#P04_configurateur",
            "port": 3000,
            "probe_url": "http://localhost:3000/",
            "description": "Site client AXESTEEL (P01 à P15) avec Configurateur 6 étapes à gauche (Modèle 1) et Assistant IA à droite (Modèle 2).",
        },
        "2_projet_dev_workbench": {
            "id": "FRONT_2_DEV",
            "label": "Projet Dev Workbench (Laboratoire Composants N1/N2/N3)",
            "url": "http://localhost:3000/#dev",
            "alias_url": "http://localhost:3000/#/dev-workbench",
            "port": 3000,
            "probe_url": "http://localhost:3000/",
            "description": "Banc d'essai isolé des composants atomiques, Mobile Lab et Galerie Maquettes.",
        },
        "3_console_pilote_ia": {
            "id": "FRONT_3_CONSOLE",
            "label": "Console Pilote IA & Observabilité V9 (4 Parties de Logs)",
            "url": "http://localhost:3000/#console",
            "alias_url": "http://localhost:3000/#/console-pilote",
            "port": 3000,
            "probe_url": "http://localhost:3000/api/v1/copilot/console/latest",
            "description": "Cockpit Console IA V9 affichant les 6 Cartes Numérotées (01 à 06), les 17 Sous-Cartes Atomiques (STP-01.1 à STP-06.3) et le Panel Inspecteur.",
        },
    },
    "backend_routes": {
        "1_projet_backend_root": {
            "id": "BACK_1_API",
            "label": "Portail Projet Backend & Sonde Health",
            "url_root": "http://127.0.0.1:8000/",
            "url_health": "http://127.0.0.1:8000/api/v1/health",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/health",
            "description": "Portail JSON récapitulatif des routes et état de santé du serveur FastAPI Clean 4-Layers.",
        },
        "2_mcp_hub_attached": {
            "id": "BACK_2_MCP",
            "label": "Hub MCP Attaché au Backend (Registre des 9 MCP & Orchestrateur #06)",
            "url_registry": "http://127.0.0.1:8000/api/v1/mcp/registry",
            "url_turn_endpoint": "http://127.0.0.1:8000/api/copilot/turn",
            "url_latest_trace": "http://127.0.0.1:8000/api/v1/copilot/console/latest",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/mcp/registry",
            "description": "Registre actif des 9 outils MCP internes rattachés au backend FastAPI et trace temps réel.",
        },
        "3_api_docs_openapi": {
            "id": "BACK_3_DOCS",
            "label": "Documentation API Interactive (Swagger UI & ReDoc)",
            "url_swagger": "http://127.0.0.1:8000/docs",
            "url_redoc": "http://127.0.0.1:8000/redoc",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/docs",
            "description": "Interface OpenAPI 3.1 pour tester toutes les routes REST, MCP et schémas Pydantic.",
        },
        "4_database_sqlite_inspector": {
            "id": "BACK_4_DB",
            "label": "Inspecteur Database SQLite WAL (batihome.db)",
            "url_inspector": "http://127.0.0.1:8000/api/v1/database",
            "url_turns_table": "http://127.0.0.1:8000/api/v1/database/tables/copilot_turns",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/database",
            "description": "Inspection directe des 8 tables SQLite WAL, compteurs de lignes et derniers enregistrements.",
        },
    },
}


@dataclass
class OsPlatformProfile:
    os_family: str
    platform_system: str
    platform_release: str
    python_executable: str
    python_version: str
    available_runtimes: Dict[str, Optional[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DetectedServiceConfig:
    service_id: str
    language: str
    framework: str
    working_dir: str
    start_command: List[str]
    port: int
    health_url: str
    dependencies_ok: bool = True
    missing_dependencies_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectBlueprintReport:
    project_root: str
    os_profile: OsPlatformProfile
    detected_services: List[DetectedServiceConfig] = field(default_factory=list)
    routes_catalog: Dict[str, Any] = field(default_factory=lambda: OFFICIAL_PROJECT_ROUTES)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_root": self.project_root,
            "os_profile": self.os_profile.to_dict(),
            "detected_services": [s.to_dict() for s in self.detected_services],
            "routes_catalog": self.routes_catalog,
        }


@dataclass
class ProcessState:
    service_id: str
    command: str
    pid: Optional[int] = None
    port: Optional[int] = None
    status: ServiceStatus = ServiceStatus.STOPPED
    uptime_seconds: float = 0.0
    start_time: Optional[float] = None
    exit_code: Optional[int] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class HealthCheckResult:
    service_id: str
    target_url: str
    is_healthy: bool
    status_code: Optional[int] = None
    latency_ms: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OverallHealthReport:
    timestamp: float = field(default_factory=time.time)
    overall_status: str = "UNKNOWN"
    services: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    checks: List[Dict[str, Any]] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorDiagnosticDigest:
    """
    Format synthétique d'erreur 'LLM-Ready' conçu pour être digéré
    immédiatement par un modèle d'IA (Cursor, Antigravity, Claude Code)
    afin de comprendre et réparer la panne sans bruit superflu.
    """
    timestamp: float = field(default_factory=time.time)
    service_id: str = "unknown"
    error_type: str = "GENERAL_FAILURE"
    command: str = ""
    exit_code: Optional[int] = None
    raw_stderr: str = ""
    clean_traceback: str = ""
    root_cause_hint: str = ""
    actionable_remedy: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# PORTS ABSTRAITS (CLEAN ARCHITECTURE)
# ============================================================================

class IProcessSupervisorPort(abc.ABC):
    """Port d'interaction multi-OS avec les processus système."""

    @abc.abstractmethod
    def clean_ports(self, ports: List[int]) -> List[int]:
        """Arrête les processus écoutant sur les ports donnés et retourne les PIDs arrêtés."""
        pass

    @abc.abstractmethod
    def spawn_service(self, service_id: str, command: List[str], cwd: str, env: Optional[Dict[str, str]] = None) -> ProcessState:
        """Démarre un sous-processus et retourne son descripteur."""
        pass

    @abc.abstractmethod
    def stop_service(self, pid: int) -> bool:
        """Arrête un sous-processus par son PID."""
        pass

    @abc.abstractmethod
    def is_pid_alive(self, pid: int) -> bool:
        """Vérifie si un PID est toujours vivant."""
        pass

    @abc.abstractmethod
    def get_open_ports(self, ports: List[int]) -> List[int]:
        """Retourne la liste des ports actuellement occupés."""
        pass


class IHealthProbePort(abc.ABC):
    """Port de sondage réseau et HTTP."""

    @abc.abstractmethod
    def check_http_health(self, service_id: str, url: str, timeout_sec: float = 2.0) -> HealthCheckResult:
        """Interroge une URL HTTP et mesure la réponse."""
        pass

    @abc.abstractmethod
    def poll_until_ready(self, probe_targets: Dict[str, str], max_wait_sec: float = 15.0) -> OverallHealthReport:
        """Sonde les cibles jusqu'à ce que toutes soient prêtes ou que le délai expire."""
        pass


class IErrorCollectorPort(abc.ABC):
    """Port d'interception et d'analyse des erreurs des services."""

    @abc.abstractmethod
    def capture_error(self, service_id: str, command: str, stderr_lines: List[str], exit_code: Optional[int] = None) -> ErrorDiagnosticDigest:
        """Analyse le flux stderr, isole la cause racine et génère le digest LLM-Ready."""
        pass

    @abc.abstractmethod
    def save_last_diagnostic(self, digest: ErrorDiagnosticDigest) -> str:
        """Sauvegarde le diagnostic dans output/last_error_diagnostic.json."""
        pass

    @abc.abstractmethod
    def get_last_diagnostic(self) -> Optional[ErrorDiagnosticDigest]:
        """Récupère le dernier diagnostic enregistré."""
        pass


class IRuntimeStatePort(abc.ABC):
    """Port de persistance de l'état runtime (PIDs actifs, statut)."""

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    def load_state(self) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def clear_state(self) -> None:
        pass


class IStackDetectorPort(abc.ABC):
    """Port d'auto-détection polyglotte de l'OS, des frameworks et des dépendances."""

    @abc.abstractmethod
    def detect_project_blueprint(self, project_root: str) -> ProjectBlueprintReport:
        pass

    @abc.abstractmethod
    def verify_and_install_dependencies(
        self, blueprint: ProjectBlueprintReport, auto_install: bool = True
    ) -> Dict[str, Any]:
        pass
