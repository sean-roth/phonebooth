---
name: qa-passes
description: Structured quality-assurance review of a body of work — specs, code, design conversations — using named pass types instead of vague "review again" prompts. Use whenever the operator asks to QA, audit, double-check, sanity-check, review for issues, or look for problems in finished work. Resist the temptation to default to a single generic scan; the point is to invoke specific pass types and let the operator combine them. Trigger on phrases like "QA pass," "audit this," "sanity check," "any drift," "look for problems," "review for X." If just "review" or "check again," ask which pass types to run before diving in.
---

# QA Passes

A structured review skill for a body of work — specs, code, design conversations, anything where the work spans multiple files or decisions and you want to find what's wrong.

This skill exists because "review again" produces vague review. Different pass types catch different problems, and naming the pass shapes what gets caught.

## When to use this skill

Use when the operator says any of:

- "Run a QA pass"
- "Audit this"
- "Sanity check before I [hand off / ship / commit]"
- "Look for [drift / inconsistencies / dead code / problems]"
- "Any issues you can see?"
- "Review again"

If the operator says something vague like "review again" or "check it once more," **do not just dive in**. Ask which pass type(s) to run. The vagueness is the problem; the skill is the response.

## The seven pass types

Each pass has a name, a question it answers, and a search heuristic. Run them individually or chain them. Tell the operator which one(s) you're running and why.

### 1. Consistency pass

**Question:** Do statements across the work agree with each other?

**Search heuristic:**
- Pick a load-bearing decision (architecture choice, API endpoint, data shape, naming convention)
- For each spec/file/section, find every reference to that decision
- Flag any disagreement, even subtle ones

**Common findings:**
- One spec says "10 leads" while another says "50 leads"
- One file uses `coaching_feedback` column; another says coaching is filesystem-based
- Spec count says "all eight" but there are nine specs

**When to run:** after major architectural pivots, after multiple edit passes, before handoff.

### 2. Traceability pass

**Question:** Does every decision in spec X get reflected in the specs that depend on it?

**Search heuristic:**
- Pick a decision point (e.g., "we added a new disposition value")
- Trace forward: every place the decision should propagate (data model, validation, UI, tests, docs)
- Flag every place it didn't propagate

**Common findings:**
- New field added to spec 03 but not spec 02 (data model)
- New event type added to logging but never referenced in the controller spec
- Frontend change made but routes spec wasn't updated

**When to run:** after adding new requirements late in design, when integrating a late spec into existing ones.

### 3. Dead-code / stale-reference pass

**Question:** Are there references to things that no longer exist or have been replaced?

**Search heuristic:**
- Identify deprecated decisions (architecture changes, removed features, replaced approaches)
- Search for any mention of the old approach
- Flag every leftover reference

**Common findings:**
- "Anthropic API" mentioned after pivot to Claude Desktop MCP
- `coaching_framework` column referenced after schema change
- "Steps 1-9" in build order after step was removed

**When to run:** after architectural pivots, after removing/replacing features, before any handoff that will be acted on.

### 4. Drift detection pass

**Question:** Has the work drifted from its original intent or constraints?

**Search heuristic:**
- Re-read the original framing/goals/constraints (if available)
- For each major decision in the current state, ask: does this serve the original goal, or did we wander?
- Flag scope creep, complexity creep, vibe drift

**Common findings:**
- "Phase 1 scope" now includes Phase 2 features
- Originally chosen for cost simplicity; ended up adding paid services
- The "minimum viable" version is now twelve files

**When to run:** late in design phase, when something feels overbuilt, when the operator says "this got bigger than I planned."

### 5. Assumption-check pass

**Question:** What load-bearing assumptions are in the work, and are any of them unverified?

**Search heuristic:**
- Read for confident statements about external systems, APIs, libraries, prices, behaviors
- For each, ask: was this verified against current sources, or is it from training memory?
- Flag the unverified ones with explicit "verify against [source]" language

**Common findings:**
- Specific API endpoint format from memory, not docs
- Pricing numbers from training data
- "X library has Y feature" without checking
- Legal compliance claims without verification

**When to run:** before any handoff to an Engineer who will hit real APIs, especially when the Designer didn't have web access.

### 6. Quality-gate pass

**Question:** Are there latent quality issues the work will produce — bad outputs, degraded UX, broken edge cases — that the spec doesn't surface?

**Search heuristic:**
- For each major output the system produces, ask: what's the quality of that output going to be?
- Trace the input pipeline backward — does everything the output needs actually arrive intact?
- Flag where data is being thrown away, mixed prematurely, or corrupted

**Common findings:**
- Stereo audio mixed to mono before processing (loses speaker attribution)
- Timestamps lost in a translation step
- Error messages user-facing but cryptic
- Transcription forced to English when audio might be Spanish

**When to run:** before build of any pipeline that produces an output the operator cares about, especially audio/video/text-processing work.

### 7. Legal-and-ethical pass

**Question:** What legal, regulatory, or ethical exposure does this work create? Is it addressed?

**Search heuristic:**
- For each user-facing action, ask: what laws or regulations might apply? (recording, data retention, privacy, accessibility, advertising claims, professional licensing)
- For each data flow, ask: is there a consent or notice obligation?
- For each automated decision, ask: who is harmed if this is wrong?
- Flag where the system creates liability that hasn't been addressed

**Common findings:**
- Recording calls in an all-party-consent state without disclosure
- Storing PII without retention policy
- Sending cold messages without unsubscribe mechanism
- AI-generated content presented as human

**When to run:** before any system goes live, before any work that touches communications/recording/health/finance/legal/employment, when there's a "we should probably check that" feeling that hasn't been checked.

## How to run a pass

1. **Confirm the pass type with the operator** if it wasn't specified. Don't run a generic "all of them" by default — that produces shallow results across the board. Pick 1-3 passes that match the situation.

2. **State which pass you're running and what you're looking for.** "Running consistency pass: looking for places different specs disagree on the disposition enum values."

3. **Search systematically, not just impressionistically.** Each pass type has a search heuristic above; use it. Don't just "look for things that seem off."

4. **Surface findings with specifics.** Not "spec 03 has issues" but "spec 03's disposition enum is missing `declined_recording` which was added to spec 10."

5. **Distinguish severity.** A typo is not the same as a load-bearing inconsistency. Tag findings as: (a) blocker — will cause the system to fail or produce wrong output, (b) friction — will slow the operator/Engineer down but not break things, (c) cosmetic — clean up if there's time.

6. **Don't auto-fix without asking.** Surface the findings, let the operator decide what to fix, what to defer, what to ignore.

## Anti-patterns to avoid

- **Running all seven passes when one was asked for.** Operator is invoking a specific tool; respect the choice.
- **Reporting "looks good!" without specifics.** Even if a pass finds nothing, name what you searched for. "Consistency pass: checked disposition enum across specs 02, 03, 07, 10 — all match. No findings."
- **Treating diminishing returns as zero returns.** A second consistency pass on the same body of work usually finds fewer things than the first, but "fewer" is not "none." Keep the standard high.
- **Conflating pass types.** "I'll do a consistency-and-drift pass" usually means doing neither well. Pick one, finish it, then pick another.
- **Skipping the legal-and-ethical pass because it feels presumptuous.** It's the most important pass for any system that touches the world. Run it whenever there's any doubt.

## Example invocations

**Operator:** "QA pass before I hand this to the Engineer."

You: "I'll run three passes: consistency, traceability, and assumption-check. Consistency to catch where specs disagree. Traceability because we made several late-stage changes that may not have propagated. Assumption-check because some specs were written from memory and the Engineer needs to know which APIs to verify. Anything else you want me to look for?"

---

**Operator:** "Anything I missed?"

You: "That's vague enough that I want to ask which type of 'missed' you mean. I can run: consistency (specs disagreeing), drift (scope creep), legal/ethical (regulatory exposure), or quality-gate (output quality). Which feels most important right now?"

---

**Operator:** "Run a legal pass on this."

You: "Running legal-and-ethical pass. I'm looking for: recording/consent obligations given the jurisdictions involved, data retention requirements, consent for AI processing, communication regulations (TCPA / DNC / CAN-SPAM equivalents), and any places the system makes claims that need licensing (legal advice, financial advice, medical claims). Confirming you want me to surface findings only, not fix them?"

## When to chain passes

Some sequences are particularly useful:

- **Pre-handoff to Engineer:** consistency → traceability → assumption-check → dead-code
- **Late-stage design crisis:** drift → consistency → legal/ethical
- **Post-pivot cleanup:** dead-code → consistency → traceability
- **Before going live:** legal/ethical → quality-gate → assumption-check
- **Field-testing review:** drift → quality-gate → legal/ethical

Run them serially, with a clear summary between each. Don't blend them.

## What this skill is NOT

- It is not a replacement for the operator's judgment. The skill surfaces findings; humans decide what matters.
- It is not a substitute for actual testing. A passing QA pass means the work is internally consistent; it doesn't mean it works.
- It is not a generic "code review." Code review checks correctness against requirements; QA passes check the requirements themselves for soundness.
- It is not for first-pass design. Use this on finished or near-finished work, not on something still being drafted.
