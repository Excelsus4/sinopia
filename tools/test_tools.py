#!/usr/bin/env python3
"""Sinopia repository and installer tests (Python 3.9+ stdlib unittest only).

Run:  python -m unittest tools/test_tools.py -v
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from typing import Callable, Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(REPO_ROOT, "skill", "sinopia")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
TEMPLATES_MD = os.path.join(SKILL_DIR, "references", "prompt_templates.md")
COMMANDS_DIR = os.path.join(REPO_ROOT, "commands")
INSTALL_PS1 = os.path.join(REPO_ROOT, "tools", "install.ps1")
INSTALL_SH = os.path.join(REPO_ROOT, "tools", "install.sh")
IS_WINDOWS = os.name == "nt"
BOM = b"\xef\xbb\xbf"
PLUGIN_FIELDS = ("name", "displayName", "version", "description", "suggestedPrompts")
EXPECTED_DESCRIPTION = ("Pre-build counsel: plain-language intake, mirror-back check, and an isolated "
                        "senior review of a refined brief. Go, Pilot, or No-Go.")
EXPECTED_PROMPTS = [
    "Review this idea with Sinopia before I start building",
    "Run Sinopia pre-build counsel on my plan and surface hidden risks",
    "Help me clarify constraints and get a Go or Pilot verdict with Sinopia",
]
SKILL_FILES = ("SKILL.md", "references/prompt_templates.md")
COMMAND_FILES = ("sinopia.md", "snp.md")

# Hangul syllables + compatibility jamo, built from code points so this file stays Hangul-free.
HANGUL_RE = re.compile("[" + chr(0xAC00) + "-" + chr(0xD7A3) + chr(0x3131) + "-" + chr(0x318E) + "]")
PLACEHOLDER_RE = re.compile(r"\{[A-Z][A-Z0-9_]*\}")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def _make_writable(func: Callable, path: str, _exc) -> None:
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    func(path)


def _rmtree(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path, onerror=_make_writable)


def _posix_bash() -> Optional[str]:
    """A POSIX bash (Git Bash / MSYS on Windows; never the WSL launcher in System32)."""
    if IS_WINDOWS:
        for cand in (r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files\Git\usr\bin\bash.exe"):
            if os.path.isfile(cand):
                return cand
        found = shutil.which("bash")
        return found if found and "system32" not in found.lower() else None
    return shutil.which("bash")


def _powershell() -> Optional[str]:
    if not IS_WINDOWS:
        return None  # install.ps1 targets Windows path conventions.
    return shutil.which("powershell") or shutil.which("pwsh")


def _posix_path(path: str) -> str:
    return path.replace("\\", "/")


def _run(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)


def _out(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout.decode("utf-8", "replace") + proc.stderr.decode("utf-8", "replace")


class TempDirCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="sinopia-test-")

    def tearDown(self) -> None:
        _rmtree(self.tmp)


# ---------------------------------------------------------------------------
# 1. skill footprint and frontmatter
# ---------------------------------------------------------------------------
def _frontmatter(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md must start with a YAML frontmatter fence"
    end = lines.index("---", 1)
    fields: Dict[str, str] = {}
    key = None
    folded: List[str] = []
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            if key is not None and folded:
                fields[key] = " ".join(folded)
            key, value = m.group(1), m.group(2).strip()
            folded = []
            if value in (">", ">-", "|", "|-"):
                fields[key] = ""
            else:
                fields[key] = value.strip("\"'")
                key = None
        elif key is not None and line.startswith((" ", "\t")):
            folded.append(line.strip())
        elif line.strip():
            raise AssertionError("unparseable frontmatter line: {!r}".format(line))
    if key is not None and folded:
        fields[key] = " ".join(folded)
    return fields


class SkillFootprintAndFrontmatterTest(unittest.TestCase):
    def test_exactly_two_skill_files(self) -> None:
        found = []
        for dirpath, dirs, files in os.walk(SKILL_DIR):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                found.append(_posix_path(os.path.relpath(os.path.join(dirpath, f), SKILL_DIR)))
        self.assertEqual(sorted(found), sorted(SKILL_FILES))

    def test_frontmatter(self) -> None:
        fm = _frontmatter(_read(SKILL_MD))
        self.assertEqual(fm.get("name"), "sinopia")
        desc = fm.get("description", "")
        self.assertTrue(desc)
        self.assertLessEqual(len(desc), 1024)
        for needle in ("/sinopia", "/snp", "Do NOT auto-trigger", "general planning requests"):
            self.assertIn(needle, desc)

    def test_relative_reference_link_exists(self) -> None:
        text = _read(SKILL_MD)
        self.assertIn("(./references/prompt_templates.md)", text)
        for target in re.findall(r"\]\((\./[^)#\s]+)\)", text):
            self.assertTrue(os.path.isfile(os.path.join(SKILL_DIR, target)), target)

    def test_commands_exist_and_reference_skill(self) -> None:
        for name in COMMAND_FILES:
            path = os.path.join(COMMANDS_DIR, name)
            self.assertTrue(os.path.isfile(path), name)
            text = _read(path)
            self.assertIn("sinopia", text)
            self.assertIn("$ARGUMENTS", text)
            self.assertTrue(text.startswith("---\n"), name)


# ---------------------------------------------------------------------------
# 2. template placeholder consistency
# ---------------------------------------------------------------------------
def _template_sections() -> Dict[str, str]:
    text = _read(TEMPLATES_MD)
    parts = re.split(r"^## ", text, flags=re.M)
    sections = {}
    for part in parts[1:]:
        title, _, body = part.partition("\n")
        sections[title.strip()] = body
    return sections


def _code_blocks(body: str) -> List[str]:
    return re.findall(r"^```[^\n]*\n(.*?)^```", body, flags=re.M | re.S)


class TemplatePlaceholderConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sections = _template_sections()
        self.legend = next(v for k, v in self.sections.items() if k.startswith("Placeholder Legend"))
        self.templates = {}
        for n in (1, 2, 3):
            key = next(k for k in self.sections if k.startswith("Template {} ".format(n)))
            blocks = _code_blocks(self.sections[key])
            self.assertEqual(len(blocks), 1, key)
            self.templates[n] = blocks[0]

    def test_used_placeholders_match_legend(self) -> None:
        legend_tokens = set(PLACEHOLDER_RE.findall(self.legend))
        used = set()
        for block in self.templates.values():
            used |= set(PLACEHOLDER_RE.findall(block))
        self.assertTrue(used)
        self.assertEqual(sorted(used - legend_tokens), [], "placeholders used but not documented")
        self.assertEqual(sorted(legend_tokens - used), [], "orphan placeholders in legend")

    def test_template2_output_headings(self) -> None:
        t2 = self.templates[2]
        for i, heading in enumerate(("Executive Verdict", "Core Specification", "Failure-Mode Defense Matrix",
                                     "Conditional Execution Matrix", "Pre-Execution QA Gates"), start=1):
            self.assertRegex(t2, r"(?m)^{}\. {}".format(i, re.escape(heading)))
        self.assertIn("{COMPLETED_SPECIALIST_BRIEF}", t2)

    def test_template3_has_verdict(self) -> None:
        self.assertIn("{VERDICT}", self.templates[3])

    def test_template1_has_five_sections(self) -> None:
        for i, heading in enumerate(("Context & Confirmed Facts", "Objectives & Required Deliverables",
                                     "Hard Constraints", "Explicit Unknowns", "Domain Failure Modes to Evaluate"),
                                    start=1):
            self.assertIn("### {}. {}".format(i, heading), self.templates[1])


# ---------------------------------------------------------------------------
# 3. isolation contract anchors
# ---------------------------------------------------------------------------
class IsolationContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = _read(SKILL_MD)

    def test_fork_forbidden(self) -> None:
        self.assertRegex(self.text, r'NEVER use `subagent_type: "fork"`')

    def test_codex_scratch_in_os_temp(self) -> None:
        self.assertIn("OS temporary directory", self.text)
        self.assertIn("never inside the target workspace", self.text)
        self.assertIn("-s read-only", self.text)

    def test_no_silent_fallback(self) -> None:
        self.assertIn("No Silent Fallback", self.text)
        self.assertIn("NEVER silently run Stage 2 inside the main conversation", self.text)

    def test_non_interactive_stop_after_mirror_back(self) -> None:
        self.assertIn("Non-Interactive Execution Guard", self.text)
        self.assertRegex(self.text, r"stop after outputting the mirror-back summary")

    def test_delivery_preferences_separated_from_constraints(self) -> None:
        self.assertIn("Delivery preference", self.text)
        self.assertIn("design constraint", self.text)
        self.assertIn("never include in the Stage-2 Brief", self.text)


# ---------------------------------------------------------------------------
# 4. public hygiene and encoding
# ---------------------------------------------------------------------------
ROOT_PUBLIC_FILES = ("README.md", "README.ko.md", "LICENSE", ".gitignore", ".gitattributes")
# Built by concatenation so this file never contains the literal tokens it forbids.
FORBIDDEN_TOKENS = tuple(a + b for a, b in (
    ("pre", "flight"), ("/coun", "cil"), ("tri", "lemma"), ("iron", "hull"), ("mal", "akh"),
    ("c:" + "\\", "projects"), ("c:/", "projects"), ("users" + "\\", "user"), ("excelsus", ".jp"),
))
FORBIDDEN_REGEXES = (re.compile(r"(?<![\w/])/" + "pf" + r"\b", re.I),)
CORE_FORBIDDEN = tuple(a + b for a, b in (("/s", "fm"), ("sfu", "mato"), ("sprez", "zatura")))


def _public_files() -> List[str]:
    out = []
    for top in ("skill", "commands", "tools"):
        for dirpath, dirs, files in os.walk(os.path.join(REPO_ROOT, top)):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
            for f in files:
                if f.endswith((".pyc", ".pyo")):
                    continue
                out.append(os.path.join(dirpath, f))
    for f in ROOT_PUBLIC_FILES:
        path = os.path.join(REPO_ROOT, f)
        if os.path.isfile(path):
            out.append(path)
    return sorted(out)


def _rel(path: str) -> str:
    return _posix_path(os.path.relpath(path, REPO_ROOT))


class PublicHygieneAndEncodingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.files = _public_files()

    def test_public_file_set_present(self) -> None:
        rels = set(_rel(p) for p in self.files)
        for need in ("skill/sinopia/SKILL.md", "skill/sinopia/references/prompt_templates.md",
                     "commands/sinopia.md", "commands/snp.md", "tools/install.ps1", "tools/install.sh",
                     "tools/test_tools.py") + ROOT_PUBLIC_FILES:
            self.assertIn(need, rels)

    def test_forbidden_strings(self) -> None:
        for path in self.files:
            lowered = _read(path).lower()
            for token in FORBIDDEN_TOKENS:
                self.assertNotIn(token, lowered, "{} contains forbidden token".format(_rel(path)))
            for rx in FORBIDDEN_REGEXES:
                self.assertIsNone(rx.search(lowered), "{} matches {}".format(_rel(path), rx.pattern))

    def test_core_independence(self) -> None:
        for path in self.files:
            if not _rel(path).startswith(("skill/", "commands/")):
                continue
            lowered = _read(path).lower()
            for token in CORE_FORBIDDEN:
                self.assertNotIn(token, lowered, "{} references a sibling project".format(_rel(path)))

    def test_english_first_purity(self) -> None:
        for path in self.files:
            if _rel(path).startswith(("skill/", "commands/", "tools/")):
                self.assertIsNone(HANGUL_RE.search(_read(path)), "{} contains Hangul".format(_rel(path)))

    def test_readme_hangul_only_in_ko_link_text(self) -> None:
        text = _read(os.path.join(REPO_ROOT, "README.md"))
        stripped = re.sub(r"\[[^\]]*\]\(\./README\.ko\.md\)", "", text)
        stripped = re.sub(r'<a\s+href="\./README\.ko\.md">[^<]*</a>', "", stripped)
        self.assertIsNone(HANGUL_RE.search(stripped), "README.md has Hangul outside the README.ko.md link")

    def test_readmes_cross_link(self) -> None:
        en = _read(os.path.join(REPO_ROOT, "README.md"))
        ko = _read(os.path.join(REPO_ROOT, "README.ko.md"))
        self.assertTrue("(./README.ko.md)" in en or 'href="./README.ko.md"' in en)
        self.assertTrue("(./README.md)" in ko or 'href="./README.md"' in ko)
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "assets", "architecture.svg")))

    def test_no_bom(self) -> None:
        for path in self.files:
            self.assertFalse(_read_bytes(path).startswith(BOM), "{} has a UTF-8 BOM".format(_rel(path)))

    def test_all_utf8(self) -> None:
        for path in self.files:
            _read_bytes(path).decode("utf-8")

    def test_install_sh_lf_only(self) -> None:
        self.assertNotIn(b"\r", _read_bytes(INSTALL_SH))
        self.assertIn("*.sh text eol=lf", _read(os.path.join(REPO_ROOT, ".gitattributes")))

    def test_license(self) -> None:
        text = _read(os.path.join(REPO_ROOT, "LICENSE"))
        self.assertIn("MIT", text)
        self.assertIn("Copyright (c) 2026 Excelsus4", text)


# ---------------------------------------------------------------------------
# 5. installer metadata parity
# ---------------------------------------------------------------------------
def _static_ps1_metadata() -> Dict:
    text = _read(INSTALL_PS1)
    sq = r"'((?:[^']|'')*)'"

    def var(name: str) -> str:
        m = re.search(r"^\$" + name + r"\s*=\s*" + sq + r"\s*$", text, re.M)
        assert m, "could not locate ${} in install.ps1".format(name)
        return m.group(1).replace("''", "'")

    block = re.search(r"^\$SuggestedPrompts\s*=\s*@\((.*?)^\)", text, re.M | re.S)
    assert block, "could not locate $SuggestedPrompts in install.ps1"
    return {"name": var("SkillName"), "displayName": var("DisplayName"), "version": var("PluginVersion"),
            "description": var("PluginDescription"),
            "suggestedPrompts": [p.replace("''", "'") for p in re.findall(sq, block.group(1))]}


def _static_sh_metadata() -> Dict:
    text = _read(INSTALL_SH)

    def var(name: str) -> str:
        m = re.search(r'^' + name + r'="([^"$`\\]*)"\s*$', text, re.M)
        assert m, "could not locate {} in install.sh".format(name)
        return m.group(1)

    return {"name": var("SKILL_NAME"), "displayName": var("DISPLAY_NAME"), "version": var("PLUGIN_VERSION"),
            "description": var("PLUGIN_DESCRIPTION"),
            "suggestedPrompts": [var("PROMPT_{}".format(i)) for i in (1, 2, 3)]}


def _load_manifest(test: unittest.TestCase, home: str) -> Dict:
    raw = _read_bytes(os.path.join(home, ".gemini", "config", "plugins", "sinopia", "plugin.json"))
    test.assertFalse(raw.startswith(BOM), "plugin.json must be UTF-8 without BOM")
    data = json.loads(raw.decode("utf-8"))
    test.assertEqual(list(data), list(PLUGIN_FIELDS))
    return data


class InstallerMetadataParityTest(TempDirCase):
    def assertCleanMetadata(self, meta: Dict, label: str) -> None:
        self.assertEqual(meta["name"], "sinopia", label)
        self.assertEqual(meta["displayName"], "Sinopia", label)
        self.assertEqual(meta["version"], "0.1.0", label)
        self.assertEqual(meta["description"], EXPECTED_DESCRIPTION, label)
        self.assertEqual(meta["suggestedPrompts"], EXPECTED_PROMPTS, label)
        self.assertLessEqual(len(meta["description"]), 140, label)
        for text in [meta[k] for k in PLUGIN_FIELDS[:4]] + list(meta["suggestedPrompts"]):
            self.assertTrue(text.isascii(), "{}: non-ASCII in {!r}".format(label, text))
            for ch in ("'", '"', "$", "`"):
                self.assertNotIn(ch, text, "{}: {!r} in {!r}".format(label, ch, text))

    def test_static_parity(self) -> None:
        ps1, sh = _static_ps1_metadata(), _static_sh_metadata()
        self.assertCleanMetadata(ps1, "install.ps1")
        self.assertCleanMetadata(sh, "install.sh")
        self.assertEqual(json.dumps(ps1).encode("utf-8"), json.dumps(sh).encode("utf-8"))

    def test_runtime_parity(self) -> None:
        results = {}
        ps = _powershell()
        if ps:
            home = os.path.join(self.tmp, "ps_home")
            proc = _run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", INSTALL_PS1,
                         "-HomeDir", home, "-Target", "agy"])
            self.assertEqual(proc.returncode, 0, _out(proc))
            results["install.ps1"] = _load_manifest(self, home)
        bash = _posix_bash()
        if bash:
            proc = _run([bash, _posix_path(INSTALL_SH), "--home", "sh_home", "--target", "agy"], cwd=self.tmp)
            self.assertEqual(proc.returncode, 0, _out(proc))
            results["install.sh"] = _load_manifest(self, os.path.join(self.tmp, "sh_home"))
        if not results:
            self.skipTest("neither PowerShell nor POSIX bash available")
        expected = json.dumps(_static_ps1_metadata()).encode("utf-8")
        for label, meta in results.items():
            self.assertCleanMetadata(meta, label)
            self.assertEqual(json.dumps(meta).encode("utf-8"), expected, label)


# ---------------------------------------------------------------------------
# 6. installer behavior (PowerShell and POSIX bash)
# ---------------------------------------------------------------------------
PS_FLAGS = {"--target": "-Target", "--agy-mode": "-AgyMode", "--dry-run": "-DryRun",
            "--source": "-Source", "--home": "-HomeDir"}


class _InstallerBehaviorBase:
    """Shared behavior mixin (not collected on its own); subclasses provide the shell runner."""

    def runner_available(self) -> bool:
        raise NotImplementedError

    def build_cmd(self, args: List[str]) -> List[str]:
        raise NotImplementedError

    def setUp(self) -> None:
        super().setUp()  # type: ignore[misc]
        if not self.runner_available():
            self.skipTest("shell not available")
        self.home = os.path.join(self.tmp, "home")

    def install(self, *args: str, home: Optional[str] = None) -> subprocess.CompletedProcess:
        return _run(self.build_cmd(["--home", home or self.home] + list(args)), cwd=self.tmp)

    def p(self, *parts: str) -> str:
        return os.path.join(self.home, *parts)

    def listing(self, root: Optional[str] = None) -> List[str]:
        root = root or self.home
        found = []
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                found.append(_posix_path(os.path.relpath(os.path.join(dirpath, f), root)))
        return sorted(found)

    def assertSkillAt(self, dest: str) -> None:
        self.assertEqual(self.listing(dest), sorted(SKILL_FILES), dest)

    def assertOk(self, proc: subprocess.CompletedProcess) -> str:
        out = _out(proc)
        self.assertEqual(proc.returncode, 0, out)
        return out

    def test_dry_run_writes_nothing(self) -> None:
        out = self.assertOk(self.install("--target", "all", "--dry-run"))
        self.assertFalse(os.path.exists(self.home))
        for frag in ("skills", "plugin.json", "suggestedPrompts", "Dry run complete"):
            self.assertIn(frag, out)

    def test_install_all(self) -> None:
        out = self.assertOk(self.install("--target", "all"))
        self.assertSkillAt(self.p(".claude", "skills", "sinopia"))
        self.assertEqual(sorted(os.listdir(self.p(".claude", "commands"))), sorted(COMMAND_FILES))
        for name in COMMAND_FILES:
            self.assertEqual(_read_bytes(self.p(".claude", "commands", name)),
                             _read_bytes(os.path.join(COMMANDS_DIR, name)))
        self.assertSkillAt(self.p(".codex", "skills", "sinopia"))
        plugin_root = self.p(".gemini", "config", "plugins", "sinopia")
        self.assertSkillAt(os.path.join(plugin_root, "skills", "sinopia"))
        self.assertEqual(sorted(os.listdir(plugin_root)), ["plugin.json", "skills"])
        self.assertFalse(os.path.exists(self.p(".gemini", "config", "skills")))
        manifest = _load_manifest(self, self.home)
        self.assertEqual(manifest["description"], EXPECTED_DESCRIPTION)
        self.assertEqual(manifest["suggestedPrompts"], EXPECTED_PROMPTS)
        self.assertEqual(_read_bytes(self.p(".claude", "skills", "sinopia", "SKILL.md")), _read_bytes(SKILL_MD))
        self.assertIn("/sinopia", out)
        self.assertIn("/snp", out)

    def test_agy_skill_mode(self) -> None:
        self.assertOk(self.install("--target", "agy", "--agy-mode", "skill"))
        self.assertSkillAt(self.p(".gemini", "config", "skills", "sinopia"))
        self.assertFalse(os.path.exists(self.p(".gemini", "config", "plugins")))

    def test_plugin_over_skill_warns_without_deleting(self) -> None:
        existing = self.p(".gemini", "config", "skills", "sinopia")
        os.makedirs(existing)
        with open(os.path.join(existing, "keep.txt"), "w", encoding="utf-8") as fh:
            fh.write("keep")
        out = self.assertOk(self.install("--target", "agy", "--agy-mode", "plugin"))
        self.assertIn("warning: skill-mode install also exists", out)
        self.assertTrue(os.path.isfile(os.path.join(existing, "keep.txt")))
        self.assertSkillAt(self.p(".gemini", "config", "plugins", "sinopia", "skills", "sinopia"))

    def test_skill_over_plugin_warns_without_deleting(self) -> None:
        self.assertOk(self.install("--target", "agy", "--agy-mode", "plugin"))
        out = self.assertOk(self.install("--target", "agy", "--agy-mode", "skill"))
        self.assertIn("warning: plugin-mode install also exists", out)
        self.assertTrue(os.path.isfile(self.p(".gemini", "config", "plugins", "sinopia", "plugin.json")))
        self.assertSkillAt(self.p(".gemini", "config", "skills", "sinopia"))

    def test_no_warning_without_opposite_mode(self) -> None:
        out = self.assertOk(self.install("--target", "agy"))
        self.assertNotIn("warning", out)

    def test_reinstall_removes_stale_files(self) -> None:
        self.assertOk(self.install("--target", "all"))
        stale = [self.p(".claude", "skills", "sinopia", "stale.txt"),
                 self.p(".codex", "skills", "sinopia", "references", "stale.md"),
                 self.p(".gemini", "config", "plugins", "sinopia", "stale.json")]
        for path in stale:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("old")
        self.assertOk(self.install("--target", "all"))
        for path in stale:
            self.assertFalse(os.path.exists(path), path)
        self.assertSkillAt(self.p(".codex", "skills", "sinopia"))

    def test_auto_detects_existing_dirs(self) -> None:
        os.makedirs(self.p(".codex"))
        os.makedirs(self.p(".gemini"))
        self.assertOk(self.install("--target", "auto"))
        self.assertSkillAt(self.p(".codex", "skills", "sinopia"))
        self.assertTrue(os.path.isfile(self.p(".gemini", "config", "plugins", "sinopia", "plugin.json")))
        self.assertFalse(os.path.exists(self.p(".claude")))

    def test_auto_falls_back_to_claude(self) -> None:
        os.makedirs(self.home)
        out = self.assertOk(self.install())
        self.assertIn("defaulting to claude", out)
        self.assertSkillAt(self.p(".claude", "skills", "sinopia"))
        self.assertFalse(os.path.exists(self.p(".codex")))
        self.assertFalse(os.path.exists(self.p(".gemini")))

    def test_bad_source_fails_cleanly(self) -> None:
        empty = os.path.join(self.tmp, "empty-src")
        os.makedirs(empty)
        proc = self.install("--target", "all", "--source", empty)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("SKILL.md not found", _out(proc))
        self.assertFalse(os.path.exists(self.home))

    def test_home_with_spaces_and_non_ascii(self) -> None:
        home = os.path.join(self.tmp, "my home dir " + chr(0xE9) + "t" + chr(0xE9))
        os.makedirs(home)
        self.assertOk(self.install("--target", "all", home=home))
        self.assertEqual(self.listing(os.path.join(home, ".claude", "skills", "sinopia")), sorted(SKILL_FILES))
        self.assertTrue(os.path.isfile(os.path.join(home, ".claude", "commands", "snp.md")))
        self.assertTrue(os.path.isfile(os.path.join(home, ".gemini", "config", "plugins", "sinopia", "plugin.json")))
        self.assertTrue(os.path.isfile(os.path.join(home, ".codex", "skills", "sinopia", "SKILL.md")))

    def test_read_only_source_reinstall(self) -> None:
        src = os.path.join(self.tmp, "ro src")
        shutil.copytree(os.path.join(REPO_ROOT, "skill"), os.path.join(src, "skill"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(COMMANDS_DIR, os.path.join(src, "commands"))
        self.make_read_only(src)
        for attempt in (1, 2, 3):
            proc = self.install("--target", "all", "--source", src)
            self.assertEqual(proc.returncode, 0, "install #{} failed:\n{}".format(attempt, _out(proc)))
        for path in (self.p(".claude", "skills", "sinopia", "SKILL.md"),
                     self.p(".claude", "skills", "sinopia", "references", "prompt_templates.md"),
                     self.p(".claude", "commands", "snp.md"),
                     self.p(".codex", "skills", "sinopia", "SKILL.md")):
            self.assertTrue(os.access(path, os.W_OK), path)

    def make_read_only(self, root: str) -> None:
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                os.chmod(os.path.join(dirpath, f), stat.S_IREAD)


class PowerShellInstallerBehaviorTest(_InstallerBehaviorBase, TempDirCase):
    def runner_available(self) -> bool:
        return _powershell() is not None

    def build_cmd(self, args: List[str]) -> List[str]:
        return [_powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", INSTALL_PS1] + \
            [PS_FLAGS.get(a, a) for a in args]


class BashInstallerBehaviorTest(_InstallerBehaviorBase, TempDirCase):
    def runner_available(self) -> bool:
        self.bash = _posix_bash()
        return self.bash is not None

    def build_cmd(self, args: List[str]) -> List[str]:
        return [self.bash, _posix_path(INSTALL_SH)] + [_posix_path(a) for a in args]

    def sh(self, script: str, check: bool = True) -> subprocess.CompletedProcess:
        proc = _run([self.bash, "-c", script], cwd=self.tmp)
        if check:
            self.assertEqual(proc.returncode, 0, _out(proc))
        return proc

    def tearDown(self) -> None:
        if getattr(self, "bash", None) and os.path.isdir(self.tmp):
            self.sh("chmod -R u+w .", check=False)
        super().tearDown()

    def make_read_only(self, root: str) -> None:
        self.sh("chmod -R a-w '{}'".format(_posix_path(os.path.relpath(root, self.tmp))))

    def test_reinstall_over_read_only_installed_copy(self) -> None:
        src = os.path.join(self.tmp, "src")
        shutil.copytree(os.path.join(REPO_ROOT, "skill"), os.path.join(src, "skill"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(COMMANDS_DIR, os.path.join(src, "commands"))
        self.sh("chmod -R a-w src")
        for attempt in (1, 2, 3):
            proc = _run([self.bash, _posix_path(INSTALL_SH), "--home", "home", "--source", "src", "--target", "all"],
                        cwd=self.tmp)
            self.assertEqual(proc.returncode, 0, "install #{} failed:\n{}".format(attempt, _out(proc)))
            if attempt == 1:
                # Simulate an older installer that left read-only copies behind.
                self.sh("chmod -R a-w home/.claude/skills/sinopia home/.claude/commands/*.md "
                        "home/.codex/skills/sinopia home/.gemini/config/plugins/sinopia")
        self.assertSkillAt(self.p(".claude", "skills", "sinopia"))
        self.assertTrue(os.access(self.p(".claude", "skills", "sinopia", "SKILL.md"), os.W_OK))
        self.assertTrue(os.access(self.p(".claude", "commands", "sinopia.md"), os.W_OK))

    def test_missing_flag_values_exit_2(self) -> None:
        for flag in ("--target", "--agy-mode", "--home", "--source"):
            with self.subTest(flag=flag):
                proc = _run([self.bash, _posix_path(INSTALL_SH), "--dry-run", flag], cwd=self.tmp)
                err = proc.stderr.decode("utf-8", "replace")
                self.assertEqual(proc.returncode, 2, err)
                self.assertIn("error: {} requires a value".format(flag), err)
        self.assertEqual(os.listdir(self.tmp), [])

    def test_invalid_values_exit_2(self) -> None:
        for args in (["--target", "nope"], ["--agy-mode", "nope"], ["--bogus"]):
            with self.subTest(args=args):
                proc = _run([self.bash, _posix_path(INSTALL_SH), "--dry-run"] + args, cwd=self.tmp)
                self.assertEqual(proc.returncode, 2, _out(proc))
                self.assertIn("error:", proc.stderr.decode("utf-8", "replace"))

    def test_help(self) -> None:
        proc = _run([self.bash, _posix_path(INSTALL_SH), "--help"], cwd=self.tmp)
        out = self.assertOk(proc)
        self.assertIn("--agy-mode", out)
        self.assertIn("--target", out)

