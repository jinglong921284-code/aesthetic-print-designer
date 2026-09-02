#!/usr/bin/env python3
"""Tests for shared Python runtime selection and the two tool runners."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import python_runtime
import run_print_tool
import run_repeat_tool


class PythonRuntimeTests(unittest.TestCase):
    def test_candidate_priority_and_no_cwd_venv_probe(self) -> None:
        with patch.object(python_runtime.shutil, "which", return_value=None):
            candidates = python_runtime.candidate_pythons(
                environ={
                    "PRINT_DESIGNER_PYTHON": "/opt/print-python",
                    "VIRTUAL_ENV": "/opt/print-venv",
                    "CONDA_PREFIX": "/opt/print-conda",
                },
                current_executable="/usr/bin/current-python",
            )
        self.assertEqual(
            candidates,
            [
                Path("/opt/print-python"),
                Path("/usr/bin/current-python"),
                Path("/opt/print-venv/bin/python3"),
                Path("/opt/print-venv/bin/python"),
                Path("/opt/print-venv/Scripts/python.exe"),
                Path("/opt/print-venv/python.exe"),
                Path("/opt/print-conda/bin/python3"),
                Path("/opt/print-conda/bin/python"),
                Path("/opt/print-conda/Scripts/python.exe"),
                Path("/opt/print-conda/python.exe"),
            ],
        )
        self.assertFalse(any(".venv" in str(path) for path in candidates))

    def test_candidates_are_de_duplicated_in_priority_order(self) -> None:
        with patch.object(python_runtime.shutil, "which", return_value=None):
            candidates = python_runtime.candidate_pythons(
                environ={"PRINT_DESIGNER_PYTHON": "/opt/shared-python"},
                current_executable="/opt/shared-python",
            )
        self.assertEqual(candidates.count(Path("/opt/shared-python")), 1)
        self.assertEqual(candidates[0], Path("/opt/shared-python"))

    def test_image_dependency_probe_imports_numpy_and_pillow(self) -> None:
        completed = SimpleNamespace(returncode=0)
        with patch.object(python_runtime.subprocess, "run", return_value=completed) as run:
            self.assertTrue(python_runtime.has_image_dependencies(Path("/opt/python")))
        self.assertEqual(
            run.call_args.args[0],
            ["/opt/python", "-c", "import numpy; from PIL import Image"],
        )

    def test_select_python_skips_missing_or_dependency_incomplete_candidates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="python-runtime-test-") as temp:
            root = Path(temp)
            missing = root / "missing-python"
            incomplete = root / "incomplete-python"
            usable = root / "usable-python"
            incomplete.write_text("", encoding="utf-8")
            usable.write_text("", encoding="utf-8")
            incomplete.chmod(0o700)
            usable.chmod(0o700)
            with patch.object(
                python_runtime,
                "candidate_pythons",
                return_value=[missing, incomplete, usable],
            ):
                with patch.object(
                    python_runtime,
                    "has_image_dependencies",
                    side_effect=[False, True],
                ) as probe:
                    selected = python_runtime.select_python(
                        require_image_dependencies=True
                    )
        self.assertEqual(selected, usable)
        self.assertEqual(probe.call_count, 2)

    def test_non_image_tool_does_not_probe_image_dependencies(self) -> None:
        with tempfile.TemporaryDirectory(prefix="python-runtime-test-") as temp:
            python = Path(temp) / "python"
            python.write_text("", encoding="utf-8")
            python.chmod(0o700)
            with patch.object(
                python_runtime,
                "candidate_pythons",
                return_value=[python],
            ):
                with patch.object(
                    python_runtime, "has_image_dependencies"
                ) as probe:
                    selected = python_runtime.select_python(
                        require_image_dependencies=False
                    )
        self.assertEqual(selected, python)
        probe.assert_not_called()

    def test_non_executable_candidate_is_skipped_for_non_image_tool(self) -> None:
        with tempfile.TemporaryDirectory(prefix="python-runtime-test-") as temp:
            root = Path(temp)
            non_executable = root / "not-executable"
            executable = root / "executable"
            non_executable.write_text("", encoding="utf-8")
            executable.write_text("", encoding="utf-8")
            non_executable.chmod(0o600)
            executable.chmod(0o700)
            with patch.object(
                python_runtime,
                "candidate_pythons",
                return_value=[non_executable, executable],
            ):
                selected = python_runtime.select_python(
                    require_image_dependencies=False
                )
        self.assertEqual(selected, executable)


class RunnerTests(unittest.TestCase):
    def test_print_runner_routes_pantone_quick_through_image_runtime(self) -> None:
        completed = SimpleNamespace(returncode=7)
        with patch.object(
            run_print_tool,
            "select_python",
            return_value=Path(sys.executable),
        ) as select:
            with patch.object(
                run_print_tool.subprocess, "run", return_value=completed
            ) as run:
                with patch.object(
                    sys,
                    "argv",
                    ["run_print_tool.py", "pantone-quick", "--help"],
                ):
                    code = run_print_tool.main()
        self.assertEqual(code, 7)
        select.assert_called_once_with(require_image_dependencies=True)
        self.assertEqual(Path(run.call_args.args[0][1]).name, "pantone_quick_match.py")

    def test_repeat_runner_uses_shared_image_runtime(self) -> None:
        completed = SimpleNamespace(returncode=0)
        with patch.object(
            run_repeat_tool,
            "select_python",
            return_value=Path(sys.executable),
        ) as select:
            with patch.object(
                run_repeat_tool.subprocess, "run", return_value=completed
            ):
                with patch.object(
                    sys, "argv", ["run_repeat_tool.py", "validate", "--help"]
                ):
                    code = run_repeat_tool.main()
        self.assertEqual(code, 0)
        select.assert_called_once_with(require_image_dependencies=True)

    def test_runner_error_mentions_portable_override(self) -> None:
        stderr = io.StringIO()
        with patch.object(run_repeat_tool, "select_python", return_value=None):
            with patch.object(
                sys, "argv", ["run_repeat_tool.py", "validate", "input.png"]
            ):
                with patch("sys.stderr", stderr):
                    code = run_repeat_tool.main()
        self.assertEqual(code, 3)
        self.assertIn("PRINT_DESIGNER_PYTHON", stderr.getvalue())
        self.assertIn("requirements.txt", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
