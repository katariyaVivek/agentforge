from src.pipeline.intent_parser import IntentManifest, ManifestEntry


def test_manifest_schema_validates_required_fields() -> None:
    entry = ManifestEntry(name="AGENT.md", reason="Core overview")
    manifest = IntentManifest(
        project_type="cli",
        domain="developer_tools",
        scale="solo",
        stack_hints=["python", "typer"],
        files_to_generate=[entry],
    )

    assert manifest.project_type == "cli"
    assert manifest.domain == "developer_tools"
    assert manifest.files_to_generate[0].name == "AGENT.md"


def test_manifest_requires_file_entry_reason() -> None:
    try:
        IntentManifest(
            project_type="cli",
            domain="dev",
            scale="solo",
            stack_hints=["python"],
            files_to_generate=[ManifestEntry(name="AGENT.md", reason="")],
        )
    except ValueError as exc:
        assert "reason" in str(exc)
