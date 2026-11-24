# Sinopia

> *Sinopia* — in Renaissance fresco painting, the red-earth underdrawing laid on rough plaster before wet lime makes every stroke irreversible.

**Ask an AI agent "should I build X?" in a field you don't know, and it answers at the level you asked** — beginner tutorials, polite hedging, and quiet guesses for everything you left unsaid.

A pre-build counsel skill for **Claude Code**, **Antigravity**, and **Codex CLI**. Sinopia interviews you in plain language, mirrors back what it understood for confirmation, distills your intent into a refined senior-to-senior brief, and sends *only* that refined brief to a fresh isolated specialist — returning a conclusion-first `Go / Conditional Go / Pilot-First / No-Go` debrief before you write code, render assets, or commit spend.

`/sinopia` · `/snp` · 2 plain-text files · zero dependencies · strictly read-only · [한국어 README](./README.ko.md)

---

## When to Run It

- **Before committing to expensive or hard-to-reverse work** — batch asset or audio generation, video production formats, new architectures, or paid integrations where fixing a wrong premise costs hours or credits.
- **When directing work outside your core specialty** — audio, visual direction, legal/contract clauses, vendor briefs, pricing, or unfamiliar stacks where casual phrasing triggers beginner-level defaults.
- **When you want a clean `Go / Pilot-First / No-Go` gate** before writing code or creating project files.

Skip it for routine bug fixes, targeted code edits, straightforward lookups, or open-ended brainstorming where direct execution is faster.

---

## Quick Start

Requires one of **Claude Code**, **Antigravity (`agy`)**, or **Codex CLI**. No Python, Node, or runtime packages are needed to run the skill itself.

### 1. Install

Clone the repository, inspect the two plain-text files in [`skill/sinopia/`](./skill/sinopia/), and run the local installer:

```bash
git clone https://github.com/Excelsus4/sinopia.git && cd sinopia

# macOS / Linux / Git Bash
bash tools/install.sh --dry-run
bash tools/install.sh --target claude                # claude | agy | codex | all | auto
bash tools/install.sh --target agy --agy-mode plugin # default for agy (or --agy-mode skill)
```

```powershell
# Windows PowerShell 5.1+ / PowerShell 7
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all
```

<details>
<summary>Manual copy alternative (no installer script)</summary>

Remove any previous `sinopia` folder before copying so `cp -r` does not nest `sinopia/sinopia`:

```bash
# Claude Code (+ /sinopia and /snp slash commands)
mkdir -p ~/.claude/skills ~/.claude/commands
rm -rf ~/.claude/skills/sinopia
cp -r skill/sinopia ~/.claude/skills/sinopia
cp commands/*.md ~/.claude/commands/

# Antigravity (agy) — skill mode (use tools/install.* for native plugin mode)
mkdir -p ~/.gemini/config/skills
rm -rf ~/.gemini/config/skills/sinopia
cp -r skill/sinopia ~/.gemini/config/skills/sinopia

# Codex CLI
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/sinopia
cp -r skill/sinopia ~/.codex/skills/sinopia
```

</details>

### 2. Run in Any Workspace

Open your agent in your target workspace (or a general session) and invoke Sinopia explicitly:

```text
/sinopia Should we add offline sync before launching our mobile MVP?
/snp I want to commission a custom sound pack — review what could go wrong before I hire anyone
```

Sinopia starts with short plain-language questions (skipping anything already documented in your workspace), mirrors back its understanding for your confirmation, runs the isolated specialist review, and stops cleanly with a decision debrief.

---

## Why an Isolated Refined Brief Beats Same-Thread Prompting

Even if you ask an LLM to *"rephrase this like an expert first, then review it"* in the same thread, the original casual prompt stays in context and keeps anchoring the answer. Sinopia puts a hard context boundary between intake and review:

| Approach | What the Reviewer Sees | Typical Failure Mode |
|---|---|---|
| **Direct prompt** (`"Should we add offline sync before launch?"`) | Casual phrasing + missing constraints | Generic pros/cons list; silently guesses team size, conflict model, and launch deadline |
| **Same-thread rephrase** (`/plan` or in-context RaR) | Rephrased spec **plus** original casual chat | Attention stays anchored to the initial framing and polite brainstorming tone |
| **Sinopia** (Stage 1 -> Stage 2 -> Stage 3) | **Only the refined senior brief** (confirmed facts, anti-goals, explicit unknowns, grounded failure modes) | Specialist focuses strictly on failure mechanisms, `If-Then` branches for open unknowns, and concrete QA gates |

---

## How It Works

1. **Stage 1 — Intake Counsel & Mirror-Back (Main Context):**
   - Silently scans workspace docs so it never asks for facts already written down.
   - Clarifies only decision-critical, user-answerable variables in plain language, keeping *delivery preferences* ("explain simply to me") separate from *design constraints* ("the end users are beginners").
   - Mirrors its understanding back in 3–6 bullets and waits for your explicit confirmation before launching Stage 2 (unless you explicitly ask to skip intake upfront).
   - Distills the confirmed intent into a dry, senior-to-senior brief with explicit `Unknowns` and grounded `Domain Failure Modes`.
2. **Stage 2 — Blind Specialist Review (Isolated Fresh Context):**
   - Spawns one fresh, read-only subagent that receives **only** the refined brief and review protocol (no raw conversation history, no `fork` inheritance, no silent main-thread fallback if isolation fails).
   - Handles every open unknown via `If-Then` branches instead of guessing, defends 1:1 against each failure mode, and marks decisions requiring live metrics or user taste as `[External Validation Required]`.
3. **Stage 3 — Grounded Debrief & Hard Stop (Main Context):**
   - Audits Stage 2 against your original intent and explicit unknowns to catch translation drift or uninvited assumptions.
   - Delivers a concise, conclusion-first briefing in your language and preferred density — then stops cleanly with zero file edits, zero plan files written, and zero commits.

---

## What You Get

Reports open with the verdict and grounding audit, followed by concrete failure-mode defenses, execution or pilot QA gates, and external-validation boundaries:

```text
Verdict: Go | Conditional Go | Pilot-First | No-Go — 1-2 line rationale
Intent & Isolation Check: confirms Stage 1/2 stayed aligned with your real goal and constraints

1. Top Failure Modes to Prevent Before Building
   - <Failure mode>: why it breaks + concrete defense rule

2. Recommended Plan & Pre-Execution QA Gates
   - Recommended approach / minimal pilot
   - 3-5 measurable pass/fail QA gates
   - Conditional branches (IF <unknown> -> THEN <action>, only if unknowns remain)

3. External-Validation Boundaries
   - Decisions requiring live metrics, pricing, or a small pilot rather than pure reasoning
```

From there, you choose the next step: build, run a small pilot, reframe and rerun Sinopia, move to divergent ideation, or drop.

---

## Scope

Sinopia is strictly a pre-decision and pre-build review skill made of **two plain-text files** ([`SKILL.md`](./skill/sinopia/SKILL.md) and [`references/prompt_templates.md`](./skill/sinopia/references/prompt_templates.md)) with zero runtime dependencies. It never modifies workspace files, creates plan documents, or commits code. It does not replace live user testing, market research, or post-build QA.

---

## Local Verification (Development)

The test suite uses Python 3.9+ standard library (`unittest`) only:

```bash
python3 -m unittest tools/test_tools.py -v
bash tools/install.sh --target all --dry-run
```

On Windows PowerShell:

```powershell
python -m unittest tools/test_tools.py -v
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all -DryRun
```

---

## Companion Tools & License

| Tool | Stage | Focus |
|---|---|---|
| **Sinopia** *(this repo)* | Pre-build | Plain-language intake + isolated senior review of a refined brief |
| **[Sfumato](https://github.com/Excelsus4/sfumato)** | Divergence | Cross-domain ideation breaking LLM homogenization |
| **[Sprezzatura](https://github.com/Excelsus4/sprezzatura)** | Post-build QA | Read-only fault-cluster audit for environment and boundary defects |

Licensed under the [MIT License](./LICENSE).
