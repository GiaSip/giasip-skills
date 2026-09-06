from pathlib import Path
import json
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "giasip-research"
SKILL = SKILL_DIR / "SKILL.md"
FEEDBACK = SKILL_DIR / "FEEDBACK.md"
README = REPO / "README.md"
ZH_SKILL = REPO / "locales" / "zh" / "skills" / "giasip-research" / "SKILL.md"
ZH_README = REPO / "locales" / "zh" / "skills" / "giasip-research" / "README.md"
CODEX_PLUGIN = REPO / "plugins" / "giasip"
CODEX_PLUGIN_MANIFEST = CODEX_PLUGIN / ".codex-plugin" / "plugin.json"
CODEX_SKILL = CODEX_PLUGIN / "skills" / "research" / "SKILL.md"
CODEX_MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
CODEX_PLUGIN_DOC = REPO / "docs" / "CODEX-PLUGIN.md"
CLAUDE_PLUGIN_MANIFEST = REPO / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"


def frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    return parts[1]


def body_after_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    return parts[2]


class GiaSipResearchPortabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
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

    def test_skill_stays_short_and_states_its_hard_rules(self) -> None:
        body = body_after_frontmatter(self.skill_text)
        # The whole point of the 2.0.0 rewrite is that this stays a short,
        # goal + hard-rules prompt, not a re-grown method document.
        self.assertLess(len(body.splitlines()), 40)
        for rule in ("source URL", "not found", "rm -rf"):
            self.assertIn(rule, self.skill_text)
        self.assertIn("FEEDBACK.md", self.skill_text)

    def test_feedback_log_exists_and_is_marked_append_only(self) -> None:
        self.assertTrue(FEEDBACK.is_file())
        text = FEEDBACK.read_text(encoding="utf-8")
        self.assertIn("append-only", text.lower())

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
        self.assertEqual("2.0.0", manifest["version"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("GiaSip Research", manifest["interface"]["displayName"])
        prompts = "\n".join(manifest["interface"]["defaultPrompt"])
        self.assertIn("$giasip:research", prompts)

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

    def test_codex_plugin_bundle_contains_only_the_research_skill(self) -> None:
        self.assertTrue(CODEX_SKILL.is_file())
        bundled_skills = sorted(
            path.name for path in (CODEX_PLUGIN / "skills").iterdir() if path.is_dir()
        )
        self.assertEqual(["research"], bundled_skills)
        bundled_text = CODEX_SKILL.read_text(encoding="utf-8")
        self.assertRegex(bundled_text, r"(?m)^name: research$")
        self.assertNotIn("$giasip-research", bundled_text)

    def test_root_and_plugin_skill_share_the_same_method_body(self) -> None:
        # The two install targets are hand-maintained copies of one method.
        # They must differ only in the frontmatter `name:` field, never in
        # the goal / method / discipline / meta-rule body.
        codex_text = CODEX_SKILL.read_text(encoding="utf-8")
        self.assertEqual(
            body_after_frontmatter(self.skill_text),
            body_after_frontmatter(codex_text),
        )

    def test_no_leftover_build_or_method_machinery(self) -> None:
        leftovers = (
            SKILL_DIR / "BUILD-PROVENANCE.json",
            SKILL_DIR / "references",
            SKILL_DIR / "scripts",
            SKILL_DIR / "agents",
            CODEX_PLUGIN / "BUILD-PROVENANCE.json",
            CODEX_PLUGIN / "skills" / "research" / "references",
            CODEX_PLUGIN / "skills" / "research" / "scripts",
            CODEX_PLUGIN / "skills" / "research" / "agents",
            REPO / "scripts" / "sync_codex_plugin.py",
            REPO / "docs" / "claim-ledger-method.md",
            REPO / "examples",
        )
        for path in leftovers:
            self.assertFalse(path.exists(), f"{path} should have been removed in the v2.0.0 rewrite")

    def test_release_docs_and_manifests_describe_both_codex_install_modes(self) -> None:
        self.assertTrue(CODEX_PLUGIN_DOC.is_file())
        required_readme_tokens = (
            "version-2.0.0",
            "codex plugin marketplace add GiaSip/giasip-skills",
            "codex plugin add giasip@giasip-skills",
            "$giasip-research",
            "$giasip:research",
            "docs/CODEX-PLUGIN.md",
        )
        for token in required_readme_tokens:
            self.assertIn(token, self.readme_text)
        for path in (CLAUDE_PLUGIN_MANIFEST, CLAUDE_MARKETPLACE):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("2.0.0", payload["version"])


if __name__ == "__main__":
    unittest.main()
