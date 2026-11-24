# Sinopia — Prompt Templates

Use these templates when executing the `sinopia` skill.

## Placeholder Legend (Replace Every Token Before Use)
- `{USER_LANGUAGE}`: The user's request language (e.g., `English`, `Korean`, `Japanese`).
- `{CRISP_TECHNICAL_TITLE}`: Dry, concise senior-level title for the decision or build under review.
- `{TARGET_DISCIPLINE}`: Concrete senior engineering, design, audio, legal, or product discipline suited to review the brief.
- `{EXACT_DOMAIN_AND_ARTIFACT}`: Exact domain and planned artifact/deliverable.
- `{ONLY_VERIFIED_FACTS_FROM_USER_AND_WORKSPACE}`: Verified facts, numbers, tools, and target-audience constraints confirmed in Stage 1 or workspace docs.
- `{CONFIRMED_PRIMARY_OBJECTIVE}`: Confirmed primary goal and measurable success criteria.
- `{WHAT_MUST_BE_AVOIDED_OR_REJECTED}`: Confirmed anti-goals and unacceptable failure outcomes.
- `{CONFIRMED_BUDGET_TIME_TOOL_PLATFORM_OR_POLICY_CONSTRAINTS}`: Confirmed hard limits on budget, timeline, tools, platform, or policy.
- `{UNKNOWN_1}`, `{UNKNOWN_2}`, `{WHY_IT_MATTERS}`: Genuinely empirical or user-deferred variables and why each changes execution.
- `{FAILURE_MODE_1_NAME}`, `{FAILURE_MODE_2_NAME}`, `{CONCRETE_MECHANISM_OF_FAILURE_IN_THIS_FIELD}`: Grounded domain failure modes to evaluate (typically 2–6; never invent filler).
- `{OPTIONAL_READONLY_FILE_ALLOWANCE}`: Empty string by default, or ` (except read-only inspection of these explicitly listed paths: <paths>)` when Stage 1 lists exact technical files.
- `{COMPLETED_SPECIALIST_BRIEF}`: The completed Template 1 output after passing the Mandatory Whole-Brief Reread.
- `{VERDICT}`: One of `Go`, `Conditional Go`, `Pilot-First`, or `No-Go`.
- `{CORE_RATIONALE}`: 1–2 line conclusion-first rationale in `{USER_LANGUAGE}`.
- `{INTENT_ALIGNMENT_NOTE}`: 1-line grounding/drift audit note in `{USER_LANGUAGE}` (plus explicit flag if Stage 1/2 drifted or softened).
- `{TRAP_NAME}`, `{FAILURE_MECHANISM_AND_DEFENSE}`: Top concrete failure modes and defenses in `{USER_LANGUAGE}`.
- `{RECOMMENDED_APPROACH}`: Concise recommended execution design or minimal pilot plan in `{USER_LANGUAGE}`.
- `{MEASURABLE_QA_GATES}`: 3–5 verifiable pre-execution / pre-publish pass-fail checks in `{USER_LANGUAGE}`.
- `{CONDITIONAL_BRANCHES}`: Remaining `IF ... -> THEN ...` branches for unresolved unknowns (omit if none).
- `{EXTERNAL_VALIDATION_ITEMS}`: Decisions that require live metrics, market taste, or a small pilot to settle in `{USER_LANGUAGE}`.

---

## Template 1 — Stage 1 Refined Specialist Brief Schema

*(Drafted privately by Stage 1 Intake Counsel after workspace pre-scan and mirror-back confirmation. Strip casual phrasing, hedging, tool names, user skill-level commentary, and Stage-3 delivery preferences. Preserve exact numbers, names, and real target-audience constraints.)*

```markdown
### Document Purpose
Senior-level pre-execution review, architecture/specification audit, and failure-mode analysis for: {CRISP_TECHNICAL_TITLE}

### 1. Context & Confirmed Facts
- **Domain / Deliverable:** {EXACT_DOMAIN_AND_ARTIFACT}
- **Confirmed Inputs, Audience & Assets:** {ONLY_VERIFIED_FACTS_FROM_USER_AND_WORKSPACE}
- **Target Goal & Success Criteria:** {CONFIRMED_PRIMARY_OBJECTIVE}
- **Anti-Goals / Explicit Non-Goals:** {WHAT_MUST_BE_AVOIDED_OR_REJECTED}

### 2. Objectives & Required Deliverables
As a senior peer specialist in {TARGET_DISCIPLINE}, produce:
1. **Go / Conditional Go / Pilot-First / No-Go Verdict** with explicit go/stop thresholds.
2. **Production / Design Specification** directly resolving the requirements and failure modes below.
3. **Conditional Branch Matrix (`If-Then`)** covering only the genuinely empirical or deferred variables listed in Section 4 without guessing.
4. **Pre-Execution / Pre-Publish QA Gates** (concrete, measurable pass/fail checks before full commitment).

### 3. Hard Constraints
- {CONFIRMED_BUDGET_TIME_TOOL_PLATFORM_OR_POLICY_CONSTRAINTS}
- Do NOT fabricate or assume unconfirmed facts; handle open parameters strictly via Section 4 `If-Then` branches.

### 4. Explicit Unknowns (Empirical or User-Deferred Only)
- **{UNKNOWN_1}:** {WHY_IT_MATTERS}
- **{UNKNOWN_2}:** {WHY_IT_MATTERS}
*(Write "None — all decision-critical parameters confirmed." if empty.)*

### 5. Domain Failure Modes to Evaluate
1. **{FAILURE_MODE_1_NAME}:** {CONCRETE_MECHANISM_OF_FAILURE_IN_THIS_FIELD}
2. **{FAILURE_MODE_2_NAME}:** {CONCRETE_MECHANISM_OF_FAILURE_IN_THIS_FIELD}
*(List only grounded, domain-specific failure mechanisms — typically 2–6; never invent filler or prescribe solutions.)*
```

---

## Template 2 — Stage 2 Blind Specialist Invocation Prompt

*(Send ONLY this prompt to a fresh, isolated subagent with zero conversation history. Never use `fork`, never include the raw user prompt or Stage-1 interview transcript, and ensure zero unresolved `{...}` tokens remain.)*

```text
You are a senior practitioner in {TARGET_DISCIPLINE} reviewing a pre-execution specification brief from a senior colleague.
Respond in {USER_LANGUAGE}. Keep the review rigorous, concrete, and densely actionable — no beginner exposition, no motivational fluff, and no hedging filler.

Operating rules:
- Pure reasoning only: do NOT call tools, read workspace files, edit files, or invent facts outside this brief{OPTIONAL_READONLY_FILE_ALLOWANCE}.
- Never silently assume answers to items listed under "Explicit Unknowns". Handle every open variable via an explicit If-Then conditional matrix.
- Explicitly defend against every item listed under "Domain Failure Modes to Evaluate".
- If any critical decision depends on external market taste, live pricing, or empirical user metrics that pure reasoning cannot settle, mark it `[External Validation Required]` and propose the smallest possible pilot test.
- Include concrete, verifiable Pre-Execution / Pre-Publish QA Gates.

Required output structure:
1. Executive Verdict (`Go` / `Conditional Go` / `Pilot-First` / `No-Go`) & core rationale
2. Core Specification / Architecture (addressing every requirement and failure mode)
3. Failure-Mode Defense Matrix (1:1 mapping against Section 5)
4. Conditional Execution Matrix (`If-Then` for Section 4 Unknowns)
5. Pre-Execution QA Gates & External-Validation Boundaries

---
{COMPLETED_SPECIALIST_BRIEF}
```

---

## Template 3 — Stage 3 Counsel Debrief Structure (User-Facing Output)

*(Synthesized in the main context after bidirectional grounding audit against the user's original intent and delivery preference. Render all section headings and body text naturally in `{USER_LANGUAGE}`.)*

```markdown
### Verdict & Grounding Check
- **Verdict:** `{VERDICT}` — {CORE_RATIONALE}
- **Intent & Isolation Check:** {INTENT_ALIGNMENT_NOTE}

---

### 1. Top Failure Modes to Prevent Before Building
- **{TRAP_NAME}:** {FAILURE_MECHANISM_AND_DEFENSE}

### 2. Recommended Plan & Pre-Execution QA Gates
- **Recommended approach:** {RECOMMENDED_APPROACH}
- **Pass/fail QA gates:** {MEASURABLE_QA_GATES}
- *(Include only if unknowns remain)* **Conditional branches:** {CONDITIONAL_BRANCHES}

### 3. External-Validation Boundaries
- {EXTERNAL_VALIDATION_ITEMS}

---
*Ask if you want the full verbatim senior specification, or let me know how you want to proceed: build, run a small pilot, reframe and rerun, move to divergent ideation, or drop.*
```
