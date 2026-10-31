#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — DÉTECTEUR UNIVERSEL POLYGLOTTE MULTI-OS & VÉRIFICATEUR DÉPENDANCES
========================================================================================
Implémente la détection automatique du système d'exploitation (Windows, Linux Debian/Ubuntu,
macOS), des runtimes installés, des frameworks du projet (Python FastAPI/Django/Flask,
Frontend Vite/Express/Next, Go, Rust, Docker) et la vérification/installation des dépendances.
100 % Bibliothèque Standard Python.
========================================================================================
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..domain.entities_and_ports import (
    IStackDetectorPort,
    OsPlatformProfile,
    DetectedServiceConfig,
    ProjectBlueprintReport,
    OFFICIAL_PROJECT_ROUTES,
)


class PolyglotStackDetectorAdapter(IStackDetectorPort):
    """Adaptateur Python pur pour auto-détecter l'OS, les stacks projet et vérifier les dépendances."""

    def detect_os_profile(self) -> OsPlatformProfile:
        sys_name = platform.system()
        release = platform.release()
        os_family = "WINDOWS" if os.name == "nt" else "LINUX_OTHER"

        if os.name != "nt":
            if sys_name == "Darwin":
                os_family = "MACOS"
            else:
                os_release_file = Path("/etc/os-release")
                if os_release_file.exists():
                    try:
                        content = os_release_file.read_text(encoding="utf-8", errors="ignore").lower()
                        if "ubuntu" in content or "debian" in content:
                            os_family = "LINUX_DEBIAN_UBUNTU"
                        elif "alpine" in content:
                            os_family = "LINUX_ALPINE"
                    except Exception:
                        pass

        is_win = os.name == "nt"
        runtimes = {
            "python": sys.executable,
            "node": shutil.which("node"),
            "npm": shutil.which("npm.cmd" if is_win else "npm") or shutil.which("npm"),
            "pnpm": shutil.which("pnpm.cmd" if is_win else "pnpm"),
            "yarn": shutil.which("yarn.cmd" if is_win else "yarn"),
            "go": shutil.which("go"),
            "cargo": shutil.which("cargo"),
            "docker": shutil.which("docker"),
        }

        return OsPlatformProfile(
            os_family=os_family,
            platform_system=sys_name,
            platform_release=release,
            python_executable=sys.executable,
            python_version=platform.python_version(),
            available_runtimes=runtimes,
        )

    def _resolve_python_bin(self, root: Path) -> str:
        is_win = os.name == "nt"
        candidates = [
            root / ".venv" / ("Scripts/python.exe" if is_win else "bin/python"),
            root / "venv" / ("Scripts/python.exe" if is_win else "bin/python"),
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        return sys.executable

    def detect_project_blueprint(self, project_root: str) -> ProjectBlueprintReport:
        root = Path(project_root).resolve()
        os_profile = self.detect_os_profile()
        python_bin = self._resolve_python_bin(root)
        is_win = os.name == "nt"
        npm_bin = os_profile.available_runtimes.get("npm") or ("npm.cmd" if is_win else "npm")

        services: List[DetectedServiceConfig] = []

        # 1. Détection Backend Python (FastAPI / Django / Flask)
        fastapi_main = root / "backend" / "entrypoints" / "api" / "main.py"
        alt_fastapi = root / "backend" / "main.py"
        django_manage = root / "manage.py"

        if fastapi_main.exists():
            deps_ok = self._check_python_imports(python_bin, ["fastapi", "uvicorn", "pydantic"])
            services.append(
                DetectedServiceConfig(
                    service_id="backend",
                    language="python",
                    framework="fastapi_uvicorn",
                    working_dir=str(root),
                    start_command=[
                        python_bin,
                        "-m",
                        "uvicorn",
                        "backend.entrypoints.api.main:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                        "--reload",
                    ],
                    port=8000,
                    health_url="http://127.0.0.1:8000/api/v1/health",
                    dependencies_ok=deps_ok,
                    missing_dependencies_hint=None
                    if deps_ok
                    else f"{python_bin} -m pip install fastapi uvicorn pydantic",
                )
            )
        elif alt_fastapi.exists():
            deps_ok = self._check_python_imports(python_bin, ["fastapi", "uvicorn"])
            services.append(
                DetectedServiceConfig(
                    service_id="backend",
                    language="python",
                    framework="fastapi_uvicorn",
                    working_dir=str(root),
                    start_command=[
                        python_bin,
                        "-m",
                        "uvicorn",
                        "backend.main:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8000",
                        "--reload",
                    ],
                    port=8000,
                    health_url="http://127.0.0.1:8000/health",
                    dependencies_ok=deps_ok,
                    missing_dependencies_hint=None if deps_ok else f"{python_bin} -m pip install -r requirements.txt",
                )
            )
        elif django_manage.exists():
            deps_ok = self._check_python_imports(python_bin, ["django"])
            services.append(
                DetectedServiceConfig(
                    service_id="backend",
                    language="python",
                    framework="django",
                    working_dir=str(root),
                    start_command=[python_bin, "manage.py", "runserver", "127.0.0.1:8000"],
                    port=8000,
                    health_url="http://127.0.0.1:8000/",
                    dependencies_ok=deps_ok,
                    missing_dependencies_hint=None if deps_ok else f"{python_bin} -m pip install django",
                )
            )

        # 2. Détection Frontend JS/TS (Vite / Express / Next / React / Vue)
        front_pkg = root / "frontend" / "package.json"
        root_pkg = root / "package.json"
        target_pkg = front_pkg if front_pkg.exists() else (root_pkg if root_pkg.exists() else None)

        if target_pkg is not None:
            front_dir = target_pkg.parent
            framework = "node_web"
            try:
                pkg_data = json.loads(target_pkg.read_text(encoding="utf-8", errors="ignore"))
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "vite" in deps and "express" in deps:
                    framework = "vite_express_tsx"
                elif "next" in deps:
                    framework = "nextjs"
                elif "vite" in deps:
                    framework = "vite_spa"
            except Exception:
                pass

            node_modules_ok = (front_dir / "node_modules").exists()
            cmd = (
                [npm_bin, "--prefix", "frontend", "run", "dev"]
                if front_dir.name == "frontend"
                else [npm_bin, "run", "dev"]
            )
            services.append(
                DetectedServiceConfig(
                    service_id="frontend",
                    language="typescript_javascript",
                    framework=framework,
                    working_dir=str(root),
                    start_command=cmd,
                    port=3000,
                    health_url="http://localhost:3000/",
                    dependencies_ok=node_modules_ok,
                    missing_dependencies_hint=None
                    if node_modules_ok
                    else f"{npm_bin} --prefix {front_dir} install",
                )
            )

        # 3. Détection Go / Rust si présents
        if (root / "go.mod").exists():
            services.append(
                DetectedServiceConfig(
                    service_id="go_service",
                    language="go",
                    framework="go_mod",
                    working_dir=str(root),
                    start_command=["go", "run", "."],
                    port=8080,
                    health_url="http://127.0.0.1:8080/health",
                    dependencies_ok=bool(os_profile.available_runtimes.get("go")),
                )
            )
        if (root / "Cargo.toml").exists():
            services.append(
                DetectedServiceConfig(
                    service_id="rust_service",
                    language="rust",
                    framework="cargo",
                    working_dir=str(root),
                    start_command=["cargo", "run"],
                    port=8080,
                    health_url="http://127.0.0.1:8080/health",
                    dependencies_ok=bool(os_profile.available_runtimes.get("cargo")),
                )
            )

        return ProjectBlueprintReport(
            project_root=str(root),
            os_profile=os_profile,
            detected_services=services,
            routes_catalog=OFFICIAL_PROJECT_ROUTES,
        )

    def _check_python_imports(self, python_bin: str, modules: List[str]) -> bool:
        stmt = f"import {', '.join(modules)}"
        try:
            proc = subprocess.run(
                [python_bin, "-c", stmt],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
            return proc.returncode == 0
        except Exception:
            return False

    def verify_and_install_dependencies(
        self, blueprint: ProjectBlueprintReport, auto_install: bool = True
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        root = Path(blueprint.project_root)

        for svc in blueprint.detected_services:
            if svc.dependencies_ok:
                results[svc.service_id] = {"status": "OK", "installed_now": False}
                continue

            if not auto_install:
                results[svc.service_id] = {
                    "status": "MISSING",
                    "installed_now": False,
                    "remedy": svc.missing_dependencies_hint,
                }
                continue

            # Auto-installation
            try:
                if svc.language == "python":
                    req_file = root / "backend" / "requirements.txt"
                    if not req_file.exists():
                        req_file = root / "requirements.txt"
                    py_bin = blueprint.os_profile.python_executable
                    cmd = (
                        [py_bin, "-m", "pip", "install", "-r", str(req_file)]
                        if req_file.exists()
                        else [py_bin, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic"]
                    )
                    proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=120, check=False)
                    svc.dependencies_ok = proc.returncode == 0
                    results[svc.service_id] = {
                        "status": "INSTALLED" if svc.dependencies_ok else "INSTALL_FAILED",
                        "installed_now": svc.dependencies_ok,
                    }
                elif svc.language == "typescript_javascript":
                    npm_bin = blueprint.os_profile.available_runtimes.get("npm") or (
                        "npm.cmd" if os.name == "nt" else "npm"
                    )
                    front_dir = root / "frontend" if (root / "frontend" / "package.json").exists() else root
                    proc = subprocess.run(
                        [npm_bin, "install"],
                        cwd=str(front_dir),
                        capture_output=True,
                        text=True,
                        timeout=180,
                        check=False,
                    )
                    svc.dependencies_ok = proc.returncode == 0
                    results[svc.service_id] = {
                        "status": "INSTALLED" if svc.dependencies_ok else "INSTALL_FAILED",
                        "installed_now": svc.dependencies_ok,
                    }
            except Exception as exc:
                results[svc.service_id] = {"status": "ERROR", "error": str(exc)}

        return results
