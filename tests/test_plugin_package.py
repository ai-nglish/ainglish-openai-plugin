"""Offline checks for the distributable OpenAI plugin package."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_manifest_identity_and_components_are_consistent():
    manifest = load_json(".codex-plugin/plugin.json")

    assert ROOT.name == manifest["name"] == "ainglish-openai-plugin"
    assert re.fullmatch(r"0\.1\.0(?:\+codex\.\d{14})?", manifest["version"])
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert manifest["repository"] == "https://github.com/ai-nglish/ainglish-openai-plugin"


def test_listing_metadata_is_complete_and_bounded():
    interface = load_json(".codex-plugin/plugin.json")["interface"]

    assert interface["displayName"] == "Ainglish"
    assert interface["privacyPolicyURL"].startswith("https://")
    assert len(interface["defaultPrompt"]) <= 3
    assert all(len(prompt) <= 128 for prompt in interface["defaultPrompt"])
    for key in ("composerIcon", "logo"):
        asset = ROOT / interface[key].removeprefix("./")
        assert asset.is_file()
        assert asset.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_remote_mcp_is_the_canonical_https_endpoint():
    servers = load_json(".mcp.json")["mcpServers"]

    assert servers == {
        "ainglish": {
            "type": "http",
            "url": "https://ainglish.org/mcp",
        }
    }


def test_skill_frontmatter_and_paths_are_provider_neutral():
    for skill_name in ("ainglish-participate", "ainglish-write"):
        path = ROOT / "skills" / skill_name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {skill_name}\n" in text.split("---", 2)[1]
        assert "CLAUDE_PLUGIN_ROOT" not in text


def test_no_legacy_claude_package_manifest_remains():
    assert not (ROOT / ".claude-plugin").exists()
