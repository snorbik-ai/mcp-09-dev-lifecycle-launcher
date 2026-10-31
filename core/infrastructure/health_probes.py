#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — SONDES DE SANTÉ RÉSEAU ET HTTP (URLLIB SANS DÉPENDANCE)
========================================================================================
Permet d'auditer la disponibilité et la latence des services BatiHome (FastAPI 8000 et Vite 3000).
========================================================================================
"""
from __future__ import annotations

import time
import urllib.request
import urllib.error
from typing import Dict, Any, List

from ..domain.entities_and_ports import IHealthProbePort, HealthCheckResult, OverallHealthReport


class HttpHealthProbeAdapter(IHealthProbePort):
    """Sonde HTTP légère utilisant urllib standard."""

    def check_http_health(self, service_id: str, url: str, timeout_sec: float = 2.0) -> HealthCheckResult:
        start_t = time.time()
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "BatiHome-HealthProbe/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                status_code = resp.getcode()
                latency_ms = (time.time() - start_t) * 1000.0
                is_healthy = 200 <= status_code < 400
                return HealthCheckResult(
                    service_id=service_id,
                    target_url=url,
                    is_healthy=is_healthy,
                    status_code=status_code,
                    latency_ms=round(latency_ms, 2)
                )
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start_t) * 1000.0
            return HealthCheckResult(
                service_id=service_id,
                target_url=url,
                is_healthy=False,
                status_code=e.code,
                latency_ms=round(latency_ms, 2),
                error_message=f"HTTP Error {e.code}: {e.reason}"
            )
        except Exception as ex:
            latency_ms = (time.time() - start_t) * 1000.0
            return HealthCheckResult(
                service_id=service_id,
                target_url=url,
                is_healthy=False,
                latency_ms=round(latency_ms, 2),
                error_message=str(ex)
            )

    def poll_until_ready(self, probe_targets: Dict[str, str], max_wait_sec: float = 15.0) -> OverallHealthReport:
        """
        Interroge en boucle les URLs cibles jusqu'à ce que 100% répondent OK
        ou que le timeout maximal soit atteint.
        """
        start_wait = time.time()
        report = OverallHealthReport()

        while (time.time() - start_wait) < max_wait_sec:
            checks: List[Dict[str, Any]] = []
            all_ok = True

            for s_id, url in probe_targets.items():
                res = self.check_http_health(s_id, url, timeout_sec=1.5)
                checks.append(res.to_dict())
                if not res.is_healthy:
                    all_ok = False

            if all_ok and len(checks) == len(probe_targets):
                report.overall_status = "HEALTHY"
                report.checks = checks
                return report

            time.sleep(0.5)

        # Timeout atteint
        report.overall_status = "DEGRADED_OR_TIMEOUT"
        report.checks = checks
        return report
