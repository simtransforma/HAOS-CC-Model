import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "scan_structural_risk.py"
SPEC = importlib.util.spec_from_file_location("scan_structural_risk", SCRIPT_PATH)
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)


def write_lines(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


class StructuralRiskScannerTests(unittest.TestCase):
    def test_cli_defaults_to_350_lines_and_markdown(self):
        args = SCANNER.build_parser().parse_args(["."])

        self.assertEqual(args.max_lines, 350)
        self.assertEqual(args.format, "markdown")

    def test_counts_and_sorts_candidates_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_lines(root / "zeta.ts", ["one", "", "three"])
            write_lines(root / "Alpha.py", ["one", "two", "three", "four"])
            write_lines(root / "small.go", ["one", "two"])

            first = SCANNER.scan_project(root, max_lines=2)
            second = SCANNER.scan_project(root, max_lines=2)

            self.assertEqual(first, second)
            self.assertEqual(
                [item["path"] for item in first["candidates"]],
                ["Alpha.py", "zeta.ts"],
            )
            self.assertEqual(first["candidates"][0]["total_lines"], 4)
            self.assertEqual(first["candidates"][1]["non_empty_lines"], 2)
            self.assertEqual(first["summary"]["scanned_files"], 3)
            self.assertEqual(first["summary"]["total_lines"], 9)
            self.assertEqual(first["summary"]["non_empty_lines"], 8)

    def test_ignores_dependencies_builds_generated_minified_and_lockfiles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_lines(root / "src" / "keep.rs", ["x", "y"])
            write_lines(root / "node_modules" / "dependency.js", ["x"] * 5)
            write_lines(root / "dist" / "bundle.js", ["x"] * 5)
            write_lines(root / "generated" / "client.ts", ["x"] * 5)
            write_lines(root / "src" / "bundle.min.js", ["x"] * 5)
            write_lines(root / "src" / "client.generated.ts", ["x"] * 5)
            write_lines(root / "Cargo.lock", ["x"] * 5)

            report = SCANNER.scan_project(root, max_lines=1)

            self.assertEqual(report["summary"]["scanned_files"], 1)
            self.assertEqual([item["path"] for item in report["candidates"]], ["src/keep.rs"])

    def test_scans_web_infrastructure_contract_and_windows_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("view.html", "theme.css", "theme.scss", "main.tf", "token.sol", "build.cmd"):
                write_lines(root / name, ["one", "two"])

            report = SCANNER.scan_project(root, max_lines=1)

            self.assertEqual(report["summary"]["scanned_files"], 6)
            self.assertEqual(
                [item["path"] for item in report["candidates"]],
                ["build.cmd", "main.tf", "theme.css", "theme.scss", "token.sol", "view.html"],
            )

    def test_cli_json_returns_zero_with_candidates_and_never_prints_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret_content = "CONTENT_MUST_NOT_APPEAR"
            write_lines(root / "app.py", [secret_content, "second"])

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    str(root),
                    "--max-lines",
                    "1",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(secret_content, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["summary"]["candidate_count"], 1)
            self.assertTrue(payload["candidates"][0]["candidate"])

    def test_output_is_opt_in_and_does_not_modify_sources_or_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "service.java"
            report_path = root / "report.md"
            write_lines(source, ["first", "second"])
            original_bytes = source.read_bytes()
            original_mtime = source.stat().st_mtime_ns

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    str(root),
                    "--max-lines",
                    "1",
                    "--format",
                    "markdown",
                    "--output",
                    str(report_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("service.java", report_path.read_text(encoding="utf-8"))
            self.assertEqual(source.read_bytes(), original_bytes)
            self.assertEqual(source.stat().st_mtime_ns, original_mtime)

            second = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(root), "--output", str(report_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already exists", second.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
