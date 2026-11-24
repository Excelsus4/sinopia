---
name: sinopia
description: >-
  Pre-build counsel for high-cost or unfamiliar-domain work. Runs a plain-language intake
  interview, mirrors back the confirmed facts, constraints, and anti-goals for explicit user
  approval, rewrites the task into a refined senior-to-senior brief (stripping casual phrasing
  and delivery preferences), sends only that refined brief to a fresh isolated specialist, and
  delivers a conclusion-first Go / Conditional Go / Pilot-First / No-Go debrief without editing
  files. Trigger ONLY when the user explicitly invokes /sinopia or /snp, or explicitly asks to
  run Sinopia. Do NOT auto-trigger on routine coding, debugging, refactoring, data lookups,
  casual questions, brainstorming, or general planning requests.
---

# Sinopia (`/sinopia`, `/snp`) — Pre-Build Counsel

Run Sinopia **before deciding to build, render, pay for, or commit to** a high-cost or unfamiliar-domain task.

## Core Principle: Sync Intake & Mirror-Back -> Isolated Senior Review -> Grounded Debrief

Prompting an LLM casually in an unfamiliar domain creates two compounding failures:
1. **Dumbing-Down & Cliche Drift:** Casual phrasing anchors the model to beginner tutorials, polite hedging, and generic checklists instead of senior production scrutiny.
2. **Silent Over-Specification:** Missing constraints are quietly filled with plausible guesses, causing expensive rework later.

**Sinopia** separates intake, specialist judgment, and final delivery across an explicit context boundary:
- **Stage 1 — Intake Counsel (Sync, Main Context):** Reads available workspace context silently, clarifies decision-critical unknowns in plain language, **mirrors back its understanding for explicit user confirmation** (unless waived upfront), and distills the confirmed intent into a refined, dry senior-to-senior **Specialist Brief** (`Confirmed Facts`, `Objectives`, `Hard Constraints`, `Explicit Unknowns`, `Domain Failure Modes`).
- **Stage 2 — Blind Specialist (Isolated Fresh Context):** Sees **only** the refined Stage-1 Brief — distilled to verified facts, constraints, unknowns, and failure modes, stripped of casual phrasing, conversation history, and delivery-style requests. Operates at senior-peer rigor to produce a `Go / Conditional Go / Pilot-First / No-Go` verdict, failure-mode defenses, conditional `If-Then` branches for open unknowns, and concrete pre-execution QA gates.
- **Stage 3 — Counsel Debrief (Main Context):** Audits Stage 2 against the user's original intent and explicit unknowns to catch translation drift or tone softening, flags external-validation boundaries, and delivers a concise, conclusion-first briefing matched to the user's preferred reading level — without modifying any files.

---

## Step-by-Step Procedure

### Stage 1 — Intake Counsel (Front-Loaded Sync)

1. **Record Language & Delivery Preference (Private — Stage 3 Only):**
   - Record `{USER_LANGUAGE}` matching the user's request language (any language: English, Korean, Japanese, etc.).
   - Distinguish **delivery preferences** from **design constraints**:
     - *Delivery preference* (e.g., "explain it simply to me", "give me a 3-line summary") -> store privately for **Stage 3 only**; never include in the Stage-2 Brief.
     - *Target-audience / design constraint* (e.g., "the end users of this app are non-technical beginners") -> **preserve** in the Stage-2 Brief as a confirmed design requirement.

2. **Pre-Scan Workspace Context (Silent, Read-Only):**
   - If invoked inside a project workspace, quickly inspect relevant docs/configs (`README.md`, architecture/decision docs, or files explicitly mentioned by the user).
   - **Rule:** Never ask the user a question whose answer is already documented in the workspace.

3. **Iterative Intake & Mandatory Mirror-Back Gate:**
   - **Never unilaterally jump to Stage 2.** Treat Stage 1 as a consultation that hands off to Stage 2 only after the user confirms the mirror-back summary (unless the user explicitly waived confirmation upfront).
   - **No fixed question quota.** Ask only the decision-critical questions needed for the current layer (0, 1, 2, or 4 — never pad to "3", never dump a 10-question form).
   - **Separate two categories of missing information (no lazy punting):**
     - **User-Answerable Unknowns** *(goals, priority trade-offs, anti-goals / what to reject, available tools/assets/budget, real workflow constraints)* -> Resolve in Stage 1. Never punt these into `Explicit Unknowns` unless the user explicitly says *"I don't know / leave it open"*.
     - **Empirical or User-Deferred Unknowns** *(unmeasured runtime metrics, future market reaction, choices the user explicitly defers)* -> Preserve in `Explicit Unknowns` for Stage 2 `If-Then` branching. Never repeat a question the user already answered with *"I don't know / leave it open"*.
   - **Loop mechanics:**
     - Ask plain-language questions in `{USER_LANGUAGE}` (translating expert variables into everyday terms, with a recommended default where helpful). If an answer opens new second-order forks or anti-goals, follow up briefly.
     - **Mirror-Back Confirmation Gate:** Once the key picture is clear, mirror your understanding back in `{USER_LANGUAGE}` using 3–6 compact bullets (goal, confirmed facts + any inference you made, hard constraints, anti-goals, and any deferred unknowns) and ask directly whether it matches their intent so you can send the refined brief for specialist review — or whether anything should be corrected or added.
     - **Correction & Exit Ramp:** If the user corrects or adds nuance, update only the changed points and re-confirm. If revisions continue past 2 mirror-back rounds, offer an explicit exit option: *"Should we keep the remaining nuances as Explicit Unknowns and run the specialist review now?"*
     - **Explicit Upfront Skip:** If the user explicitly asks to skip intake/confirmation and review immediately, show a compact recap without waiting for confirmation, demote every unconfirmed inference into `Explicit Unknowns` (never silently assume it), and note in 1 line how many open unknowns are being carried forward.
     - **Non-Interactive Execution Guard:** If running in a non-interactive environment (`claude -p`, `codex exec`, `agy -p`, or automated pipelines) where no interactive user reply is possible, **stop after outputting the mirror-back summary and the draft Specialist Brief**; do NOT launch Stage 2 without confirmation unless explicitly waived in the prompt.

4. **Draft the Refined Specialist Brief (Private — Follow [prompt_templates.md](./references/prompt_templates.md)):**
   - Populate all placeholders defined in [prompt_templates.md](./references/prompt_templates.md) (`{CRISP_TECHNICAL_TITLE}`, `{TARGET_DISCIPLINE}`, `{USER_LANGUAGE}`, and all brief sections).
   - Write the Brief in dry, neutral senior-peer prose (English or formal colloquial-free technical `{USER_LANGUAGE}`) containing all 5 sections:
     1. `Context & Confirmed Facts` *(verified user answers + workspace facts only; preserve exact numbers, product names, and audience constraints)*
     2. `Objectives & Required Deliverables`
     3. `Hard Constraints`
     4. `Explicit Unknowns` *(genuinely empirical or user-deferred variables only)*
     5. `Domain Failure Modes to Evaluate` *(only grounded failure mechanisms specific to this domain — typically 2–6; never invent filler for simple cases, and never prescribe solutions)*
   - **Mandatory Whole-Brief Reread (Before Spawning Stage 2):**
     - [ ] Zero raw casual user phrasing, hedging, or emotional venting?
     - [ ] Zero delivery-style requests ("explain simply") leaked in, while real target-audience constraints remain intact?
     - [ ] Zero meta-framing about the tool or user skill level (never mention "Sinopia" or "translated from a beginner prompt")?
     - [ ] Zero unresolved `{...}` template placeholders remaining?
     - [ ] Zero unverified assumptions masquerading as confirmed facts, and zero pre-cooked solutions injected?

---

### Stage 2 — Blind Specialist Review (Isolated Fresh Context)

Launch **1 isolated, fresh-context subagent** passing **only** Template 2 + the completed Specialist Brief from [prompt_templates.md](./references/prompt_templates.md).

| Host | Isolation Invocation |
|---|---|
| **Claude Code** | Use the `Agent` tool with a **fresh non-fork subagent** (e.g., `general-purpose`, read-only). **NEVER use `subagent_type: "fork"`** (fork inherits the parent conversation and breaks isolation). Pass only Template 2 + Brief. |
| **Antigravity (`agy`)** | Use `invoke_subagent` with `TypeName: "research"`, `Model: "inherit"`. Pass only Template 2 + Brief; forbid reading workspace files unless Stage 1 explicitly lists specific read-only technical paths. |
| **Codex CLI** | Write the prompt only to an **OS temporary directory** (never inside the target workspace) and run `codex exec --skip-git-repo-check -C <tempdir> -s read-only` so workspace `AGENTS.md` is not inherited. Delete the temp file immediately after Stage 3. |

**Hard Isolation & Honest Failure Rules:**
- Stage 2 receives **only** the refined Brief + Template 2 — never the raw user prompt, Stage-1 interview transcript, or Stage-3 delivery preference.
- **No Silent Fallback (Fake Blindness Forbidden):** If the host cannot spawn an isolated fresh context or the subagent call fails, **NEVER silently run Stage 2 inside the main conversation while pretending it was isolated.** Stop, disclose that isolated execution is unavailable, return the confirmed Brief, and ask the user whether they want to stop or proceed explicitly in degraded (non-isolated) mode.
- Stage 2 must not fabricate answers for `Explicit Unknowns` (use `If-Then` branches), must tag decisions requiring market taste, live pricing, or empirical user metrics as `[External Validation Required]`, and must output verifiable Pre-Execution QA Gates.

---

### Stage 3 — Counsel Debrief & Grounding Audit (Main Context)

When Stage 2 returns, do **not** dump the raw dense report blindly. Audit it and deliver a crisp debrief in `{USER_LANGUAGE}` using Template 3 from [prompt_templates.md](./references/prompt_templates.md) (rendering all section headings naturally in `{USER_LANGUAGE}`):

1. **Bidirectional Grounding & Drift Audit:**
   - **Intent check:** Verify Stage 1 did not drop or distort the user's real goal, constraints, or anti-goals. If restoring a missed constraint would change the verdict, flag it explicitly and offer to rerun Stage 2 with the corrected Brief.
   - **Unknowns & isolation check:** Verify Stage 2 did not quietly invent answers for `Explicit Unknowns` and did not soften into beginner tutorial tone (which can signal host-level global instruction bleed).
2. **Conclusion-First Delivery (Matched to User's Preferred Density):**
   - Lead with the `Go / Conditional Go / Pilot-First / No-Go` verdict and 1–2 line rationale.
   - Summarize the top failure modes and concrete defenses, recommended execution or minimal pilot plan with measurable QA gates, any remaining `If-Then` branches, and external-validation boundaries.
   - Offer to display the full verbatim Stage-2 technical specification if requested.
3. **Hard Stop Before Building (Chat-Only Output):**
   - Sinopia is strictly a **pre-decision / pre-build review skill**.
   - **NEVER** create or edit project files (including plan/spec markdown files in the workspace), run pilots, spend paid credits, or commit/push during Sinopia. (OS temp files created solely for Codex Stage-2 invocation must be deleted immediately.)
   - End cleanly so the user chooses the next step: **Proceed to build**, **Run a small pilot**, **Reframe and rerun Sinopia**, **Move to a divergent ideation workflow**, or **Drop**.

---

## Non-Goals (When NOT to Use `/sinopia`)
- Routine bug fixes, targeted code edits, refactoring, or straightforward data lookups where direct execution is already strong.
- Open-ended creative divergence where you want radical cross-domain ideas (run Sinopia first to clarify constraints if needed, then switch to a divergent ideation workflow).
- Multi-stakeholder or multi-model governance debates inside an active project.

## Validation Checklist
- [ ] Workspace context was inspected silently before asking any user question.
- [ ] Stage 1 clarified user-answerable forks without padding questions and completed the mirror-back confirmation gate (or recorded an explicit upfront skip with unconfirmed inferences demoted to `Explicit Unknowns`).
- [ ] Stage-2 Brief passed whole-brief reread: zero raw casual phrasing, zero delivery preferences, zero tool/skill-level meta-framing, zero unresolved `{...}` tokens, and grounded failure modes only.
- [ ] Stage 2 ran in an isolated fresh context (no `fork`, no workspace scratch files, no silent main-thread fallback on failure).
- [ ] Stage 3 performed bidirectional grounding/drift audit, rendered headings and prose naturally in `{USER_LANGUAGE}`, and left the workspace completely unmodified.
