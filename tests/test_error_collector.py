#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import tempfile
import shutil
from pathlib import Path
from core.infrastructure.error_collector import ErrorCollectorAdapter


class TestErrorCollector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.collector = ErrorCollectorAdapter(output_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_module_not_found_detection(self):
        raw_lines = [
            "Traceback (most recent call last):",
            "  File 'main.py', line 1, in <module>",
            "ModuleNotFoundError: No module named 'fastapi'"
        ]
        digest = self.collector.capture_error("backend", "python main.py", raw_lines, 1)
        self.assertEqual(digest.error_type, "PYTHON_MODULE_NOT_FOUND")
        self.assertIn("fastapi", digest.root_cause_hint)
        self.assertIn("pip install fastapi", digest.actionable_remedy)

    def test_eaddrinuse_detection(self):
        raw_lines = [
            "node:events:505",
            "Error: listen EADDRINUSE: address already in use :::3000"
        ]
        digest = self.collector.capture_error("frontend", "npm run dev", raw_lines, 1)
        self.assertEqual(digest.error_type, "PORT_CONFLICT_EADDRINUSE")
        self.assertIn("3000", digest.root_cause_hint)


if __name__ == "__main__":
    unittest.main()
