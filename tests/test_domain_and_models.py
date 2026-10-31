#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from core.domain.entities_and_ports import (
    ProcessState,
    ServiceStatus,
    HealthCheckResult,
    ErrorDiagnosticDigest,
    OverallHealthReport,
    OFFICIAL_PROJECT_ROUTES,
)
from core.infrastructure.stack_detector import PolyglotStackDetectorAdapter


class TestDomainEntities(unittest.TestCase):
    def test_process_state_serialization(self):
        ps = ProcessState(
            service_id="backend",
            command="uvicorn ...",
            pid=1234,
            status=ServiceStatus.HEALTHY
        )
        d = ps.to_dict()
        self.assertEqual(d["service_id"], "backend")
        self.assertEqual(d["pid"], 1234)
        self.assertEqual(d["status"], "HEALTHY")

    def test_error_diagnostic_digest(self):
        diag = ErrorDiagnosticDigest(
            service_id="backend",
            error_type="PORT_CONFLICT",
            root_cause_hint="Port 8000 busy",
            actionable_remedy="Free port 8000"
        )
        d = diag.to_dict()
        self.assertEqual(d["error_type"], "PORT_CONFLICT")
        self.assertIn("Port 8000", d["root_cause_hint"])

    def test_official_7_routes_and_polyglot_detector(self):
        self.assertEqual(len(OFFICIAL_PROJECT_ROUTES["frontend_routes"]), 3)
        self.assertEqual(len(OFFICIAL_PROJECT_ROUTES["backend_routes"]), 4)
        detector = PolyglotStackDetectorAdapter()
        project_root = str(Path(__file__).resolve().parents[3])
        blueprint = detector.detect_project_blueprint(project_root)
        self.assertIn(blueprint.os_profile.os_family, ("WINDOWS", "LINUX_DEBIAN_UBUNTU", "LINUX_OTHER", "MACOS"))
        service_ids = [s.service_id for s in blueprint.detected_services]
        self.assertIn("backend", service_ids)
        self.assertIn("frontend", service_ids)


if __name__ == "__main__":
    unittest.main()
