from pathlib import Path
import json
import re
import subprocess
import sys
import unittest


REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "giasip-research"
SKILL = SKILL_DIR / "SKILL.md"
FACT_CHECK = SKILL_DIR / "references" / "fact-check-protocol.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
README = REPO / "README.md"
ZH_SKILL = REPO / "locales" / "zh" / "skills" / "giasip-research" / "SKILL.md"
ZH_README = REPO / "locales" / "zh" / "skills" / "giasip-research" / "README.md"
CODEX_PLUGIN = REPO / "plugins" / "giasip"
CODEX_PLUGIN_MANIFEST = CODEX_PLUGIN / ".codex-plugin" / "plugin.json"
CODEX_SKILL = CODEX_PLUGIN / "skills" / "research" / "SKILL.md"
CODEX_OPENAI_YAML = CODEX_PLUGIN / "skills" / "research" / "agents" / "openai.yaml"
CODEX_MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
CODEX_SYNC_SCRIPT = REPO / "scripts" / "sync_codex_plugin.py"
CODEX_PLUGIN_DOC = REPO / "docs" / "CODEX-PLUGIN.md"
CLAUDE_PLUGIN_MANIFEST = REPO / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"


def frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    return parts[1]


class GiaSipResearchPortabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.fact_check_text = FACT_CHECK.read_text(encoding="utf-8")
        cls.readme_text = README.read_text(encoding="utf-8")

    def test_frontmatter_uses_portable_discovery_contract(self) -> None:
        yaml = frontmatter(self.skill_text)
        keys = {
            match.group(1)
            for line in yaml.splitlines()
            if (match := re.match(r"^([a-zA-Z][a-zA-Z0-9_-]*):", line))
        }
        self.assertEqual({"name", "description"}, keys)
        self.assertRegex(yaml, r"(?m)^name: giasip-research$")
        self.assertRegex(yaml, r'(?m)^description: ["\']?Use when')

    def test_skill_is_self_contained_and_has_no_personal_paths(self) -> None:
        forbidden = (
            "/Users/haox",
            "~/agent-skills",
            "research-parallel",
            "research-portable",
        )
        for token in forbidden:
            self.assertNotIn(token, self.skill_text)

    def test_standalone_keeps_both_mappings_and_plugin_is_codex_native(self) -> None:
        codex_text = CODEX_SKILL.read_text(encoding="utf-8")
        self.assertIn("Claude Code Runtime Contract", self.skill_text)
        self.assertIn("WebSearch", self.skill_text)
        self.assertIn("Codex Standalone Runtime Contract", self.skill_text)
        self.assertIn("Codex Runtime Contract", codex_text)
        self.assertIn("callable collaboration schema", codex_text)
        self.assertNotIn("Claude Code Runtime Contract", codex_text)

    def test_mini_assurance_has_an_explicit_no_slot_fallback(self) -> None:
        required = ("fresh worker slot", "idle independent worker", "non-independent fallback")
        for token in required:
            self.assertIn(token, self.fact_check_text)

    def test_all_referenced_markdown_files_exist_inside_skill(self) -> None:
        referenced = set(
            re.findall(r"references/[a-z0-9-]+\.md", self.skill_text)
        )
        self.assertTrue(referenced, "SKILL.md should link to bundled references")
        for relative in referenced:
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)

    def test_standalone_metadata_preserves_giasip_brand_and_invocation(self) -> None:
        self.assertTrue(OPENAI_YAML.is_file(), "agents/openai.yaml is required")
        metadata = OPENAI_YAML.read_text(encoding="utf-8")
        self.assertIn('display_name: "GiaSip Research"', metadata)
        self.assertIn("$giasip-research", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_readme_documents_both_install_and_invocation_surfaces(self) -> None:
        required = (
            "--agent codex",
            "$giasip-research",
            "/giasip-research",
            "Claude Code",
            "Codex",
        )
        for token in required:
            self.assertIn(token, self.readme_text)

    def test_chinese_reading_edition_cannot_be_discovered_as_a_second_skill(self) -> None:
        self.assertFalse(ZH_SKILL.exists(), "Chinese reading edition must not be a second installable SKILL.md")
        self.assertTrue(ZH_README.is_file())
        text = ZH_README.read_text(encoding="utf-8")
        self.assertIn("skills/giasip-research/SKILL.md", text)
        self.assertIn("$giasip-research", text)
        self.assertIn("/giasip-research", text)

    def test_codex_plugin_manifest_uses_giasip_namespace(self) -> None:
        self.assertTrue(CODEX_PLUGIN_MANIFEST.is_file())
        manifest = json.loads(CODEX_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("giasip", manifest["name"])
        self.assertEqual("1.6.1", manifest["version"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("GiaSip Research", manifest["interface"]["displayName"])
        prompts = "\n".join(manifest["interface"]["defaultPrompt"])
        self.assertIn("$giasip:research", prompts)

    def test_generated_targets_share_one_canonical_provenance(self) -> None:
        standalone = json.loads(
            (SKILL_DIR / "BUILD-PROVENANCE.json").read_text(encoding="utf-8")
        )
        codex = json.loads(
            (CODEX_PLUGIN / "BUILD-PROVENANCE.json").read_text(encoding="utf-8")
        )
        self.assertEqual("standalone", standalone["profile"])
        self.assertEqual("codex", codex["profile"])
        self.assertEqual(standalone["source_hashes"], codex["source_hashes"])
        self.assertEqual(standalone["semantic_contract"], codex["semantic_contract"])
        self.assertIn("hypothesis-spine", standalone["semantic_contract"])

    def test_repo_marketplace_exposes_only_the_codex_ready_plugin(self) -> None:
        self.assertTrue(CODEX_MARKETPLACE.is_file())
        marketplace = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8"))
        self.assertEqual("giasip-skills", marketplace["name"])
        self.assertEqual(1, len(marketplace["plugins"]))
        entry = marketplace["plugins"][0]
        self.assertEqual("giasip", entry["name"])
        self.assertEqual("./plugins/giasip", entry["source"]["path"])
        self.assertEqual("AVAILABLE", entry["policy"]["installation"])
        self.assertEqual("ON_INSTALL", entry["policy"]["authentication"])

    def test_codex_plugin_bundle_is_generated_from_the_canonical_skill(self) -> None:
        self.assertTrue(CODEX_SYNC_SCRIPT.is_file())
        result = subprocess.run(
            [sys.executable, str(CODEX_SYNC_SCRIPT), "--check"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        bundled_skills = sorted(
            path.name for path in (CODEX_PLUGIN / "skills").iterdir() if path.is_dir()
        )
        self.assertEqual(["research"], bundled_skills)
        bundled_text = CODEX_SKILL.read_text(encoding="utf-8")
        self.assertRegex(bundled_text, r"(?m)^name: research$")
        bundle_copy = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((CODEX_PLUGIN / "skills" / "research").rglob("*"))
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}
        )
        self.assertIn("$giasip:research", bundle_copy)
        invocation_surface = bundled_text + CODEX_OPENAI_YAML.read_text(encoding="utf-8")
        self.assertNotIn("$giasip-research", invocation_surface)

    def test_checked_in_skill_is_declared_generated_not_a_second_source(self) -> None:
        self.assertIn("Generated from the neutral canonical Research method", self.skill_text)
        self.assertIn("Do not edit this target by hand", self.skill_text)

    def test_release_docs_and_manifests_describe_both_codex_install_modes(self) -> None:
        self.assertTrue(CODEX_PLUGIN_DOC.is_file())
        required_readme_tokens = (
            "version-1.6.1",
            "codex plugin marketplace add GiaSip/giasip-skills",
            "codex plugin add giasip@giasip-skills",
            "$giasip-research",
            "$giasip:research",
            "docs/CODEX-PLUGIN.md",
        )
        for token in required_readme_tokens:
            self.assertIn(token, self.readme_text)
        plugin_doc = CODEX_PLUGIN_DOC.read_text(encoding="utf-8")
        self.assertIn("scripts/sync_codex_plugin.py --canonical-root", plugin_doc)
        self.assertIn("--check", plugin_doc)
        self.assertIn("giasip-dispatch", plugin_doc)
        self.assertIn("not bundled", plugin_doc)
        for path in (CLAUDE_PLUGIN_MANIFEST, CLAUDE_MARKETPLACE):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("1.6.1", payload["version"])


if __name__ == "__main__":
    unittest.main()
