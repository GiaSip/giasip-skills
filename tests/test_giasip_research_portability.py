from pathlib import Path
import re
import unittest


REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "giasip-research"
SKILL = SKILL_DIR / "SKILL.md"
FACT_CHECK = SKILL_DIR / "references" / "fact-check-protocol.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
README = REPO / "README.md"
ZH_SKILL = REPO / "locales" / "zh" / "skills" / "giasip-research" / "SKILL.md"
ZH_README = REPO / "locales" / "zh" / "skills" / "giasip-research" / "README.md"


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

    def test_skill_defines_both_host_runtime_mappings(self) -> None:
        required = (
            "Claude Code runtime",
            "Codex runtime",
            "spawn_agent",
            "WebSearch",
            "WebFetch",
            "sequential",
            "callable schema",
        )
        for token in required:
            self.assertIn(token, self.skill_text)

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

    def test_codex_metadata_preserves_giasip_brand_and_invocation(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
