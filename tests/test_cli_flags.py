import os

from typer.testing import CliRunner

from src.main import app


os.environ.setdefault("GSD_TEST_MODE", "1")
runner = CliRunner()


def test_generate_command_dry_run() -> None:
    result = runner.invoke(app, ["--dry-run", "build a custom CLI"])
    assert "Dry run complete" in result.stdout


def test_generate_verbose_outputs_manifest_json() -> None:
    result = runner.invoke(app, ["--verbose", "build a custom CLI"])
    assert result.exit_code == 0
    assert "files_to_generate" in result.stdout
