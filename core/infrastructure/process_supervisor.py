#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — SUPERVISEUR DE PROCESSUS MULTI-OS (WINDOWS & UBUNTU LINUX)
========================================================================================
Implémente le contrôle des processus et la libération des ports pour Windows (Win32 API/taskkill)
et Linux Ubuntu (POSIX signals/fuser/kill).
========================================================================================
"""
from __future__ import annotations

import os
import sys
import socket
import signal
import subprocess
import threading
import time
from typing import Dict, Any, List, Optional

from ..domain.entities_and_ports import IProcessSupervisorPort, ProcessState, ServiceStatus


class MultiOsProcessSupervisor(IProcessSupervisorPort):
    """Adaptateur concret gérant le cycle de vie des sous-processus de façon multiplateforme."""

    def __init__(self):
        self.is_windows = os.name == "nt"
        self._running_processes: Dict[str, subprocess.Popen] = {}
        self._captured_logs: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def get_open_ports(self, ports: List[int]) -> List[int]:
        """Vérifie quels ports sont actuellement à l'écoute sur 127.0.0.1."""
        occupied = []
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                res = s.connect_ex(("127.0.0.1", port))
                if res == 0:
                    occupied.append(port)
        return occupied

    def clean_ports(self, ports: List[int]) -> List[int]:
        """Arrête de force les processus occupant les ports spécifiés."""
        freed_pids = []
        if self.is_windows:
            for port in ports:
                pids = self._find_pids_windows(port)
                for pid in pids:
                    if pid > 4:  # Protéger System (PID 4) et Idle (PID 0)
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/T", "/PID", str(pid)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False
                            )
                            freed_pids.append(pid)
                        except Exception:
                            pass
        else:
            # POSIX / Ubuntu Linux
            for port in ports:
                try:
                    # Utilisation de fuser pour libérer le port TCP
                    subprocess.run(
                        ["fuser", "-k", f"{port}/tcp"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False
                    )
                except Exception:
                    pass
        time.sleep(0.5)
        return list(set(freed_pids))

    def _find_pids_windows(self, port: int) -> List[int]:
        """Trouve les PIDs associés à un port TCP sous Windows via netstat."""
        pids = []
        try:
            cmd = ["netstat", "-ano", "-p", "tcp"]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            pattern = f":{port} "
            for line in proc.stdout.splitlines():
                if pattern in line and "LISTENING" in line:
                    parts = line.strip().split()
                    if parts:
                        pid_candidate = parts[-1]
                        if pid_candidate.isdigit():
                            pids.append(int(pid_candidate))
        except Exception:
            pass
        return list(set(pids))

    def spawn_service(
        self,
        service_id: str,
        command: List[str],
        cwd: str,
        env: Optional[Dict[str, str]] = None
    ) -> ProcessState:
        """Lance un sous-processus et initialise la capture de ses flux de sortie."""
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        creation_flags = 0
        if self.is_windows:
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        with self._lock:
            self._captured_logs[service_id] = []

        proc = subprocess.Popen(
            command,
            cwd=cwd,
            env=full_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=creation_flags
        )

        with self._lock:
            self._running_processes[service_id] = proc

        # Démarrer un thread dédié de lecture continue pour éviter le blocage du pipe
        t = threading.Thread(
            target=self._drain_output,
            args=(service_id, proc),
            daemon=True,
            name=f"log-drainer-{service_id}"
        )
        t.start()

        return ProcessState(
            service_id=service_id,
            command=" ".join(command),
            pid=proc.pid,
            status=ServiceStatus.STARTING,
            start_time=time.time()
        )

    def _drain_output(self, service_id: str, proc: subprocess.Popen):
        """Lit en continu stdout/stderr et conserve les 200 dernières lignes."""
        try:
            if proc.stdout:
                for line in iter(proc.stdout.readline, ''):
                    if not line:
                        break
                    clean_line = line.strip()
                    if clean_line:
                        with self._lock:
                            logs = self._captured_logs.setdefault(service_id, [])
                            logs.append(clean_line)
                            if len(logs) > 200:
                                self._captured_logs[service_id] = logs[-200:]
        except Exception:
            pass

    def get_recent_logs(self, service_id: str, max_lines: int = 50) -> List[str]:
        """Retourne les dernières lignes de log capturées pour le service."""
        with self._lock:
            logs = self._captured_logs.get(service_id, [])
            return list(logs[-max_lines:])

    def stop_service(self, pid: int) -> bool:
        """Arrête un processus par son PID de façon multiplateforme."""
        if pid <= 0:
            return False

        # 1. Tenter d'abord d'arrêter via le descripteur Popen en mémoire si c'est un processus enfant
        with self._lock:
            for s_id, proc in list(self._running_processes.items()):
                if proc.pid == pid:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1.0)
                        return True
                    except Exception:
                        try:
                            proc.kill()
                            return True
                        except Exception:
                            pass

        # 2. Tenter l'arrêt système via taskkill (Windows) ou signal (Linux)
        try:
            if self.is_windows:
                res = subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                if res.returncode == 0:
                    return True
                # Fallback PowerShell si taskkill direct échoue
                ps_res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                return ps_res.returncode == 0
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                if self.is_pid_alive(pid):
                    os.kill(pid, signal.SIGKILL)
                return True
        except Exception:
            return False

    def is_pid_alive(self, pid: int) -> bool:
        """Vérifie si un processus est actif."""
        if pid <= 0:
            return False
        if self.is_windows:
            try:
                proc = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return str(pid) in proc.stdout
            except Exception:
                return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
