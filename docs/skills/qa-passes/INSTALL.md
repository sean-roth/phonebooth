# Installing the qa-passes skill in Claude Desktop

The `SKILL.md` in this folder is a Claude Desktop skill — a reusable instruction set that activates when you (or Engineer Claude) ask for QA review work. This guide walks you through installing it.

## What this skill does

Replaces vague "review again" prompts with seven named pass types: consistency, traceability, dead-code/stale-reference, drift, assumption-check, quality-gate, and legal-and-ethical. Each pass has a search heuristic and common findings to look for.

The skill is documented in `SKILL.md` in this folder. Read it once before installing.

## Installation

### macOS

Claude Desktop's skills folder lives at:

```
~/Library/Application Support/Claude/skills/
```

Create the skill folder and copy the SKILL.md:

```bash
mkdir -p ~/Library/Application\ Support/Claude/skills/qa-passes
curl -o ~/Library/Application\ Support/Claude/skills/qa-passes/SKILL.md \
  https://raw.githubusercontent.com/sean-roth/phonebooth/main/docs/skills/qa-passes/SKILL.md
```

Restart Claude Desktop.

### Linux (OptiPlex)

The skills folder location depends on Claude Desktop's Linux build, but conventionally:

```
~/.config/Claude/skills/
```

If that path doesn't exist, check Claude Desktop's settings or look for where other skills live (you mentioned having a `metacognition-system` skill installed; finding that folder reveals the right location).

Once you find it:

```bash
mkdir -p ~/.config/Claude/skills/qa-passes
curl -o ~/.config/Claude/skills/qa-passes/SKILL.md \
  https://raw.githubusercontent.com/sean-roth/phonebooth/main/docs/skills/qa-passes/SKILL.md
```

Restart Claude Desktop.

### Windows

```
%APPDATA%\Claude\skills\
```

In PowerShell:

```powershell
$skillDir = "$env:APPDATA\Claude\skills\qa-passes"
New-Item -ItemType Directory -Force -Path $skillDir
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/sean-roth/phonebooth/main/docs/skills/qa-passes/SKILL.md" `
  -OutFile "$skillDir\SKILL.md"
```

Restart Claude Desktop.

## Verifying installation

After restarting Claude Desktop, start a new conversation and say:

> "Run a QA pass on this short list of items: [list a few things, like a short spec or a few sentences with intentional inconsistency]. Specifically, run a consistency pass."

If the skill is loaded correctly, Claude will:

1. State which pass it's running and what it's looking for
2. Search systematically using the consistency pass heuristic
3. Surface findings with severity tags (blocker / friction / cosmetic)

If Claude just does a generic review without naming the pass type or following the heuristic, the skill isn't loaded — restart Claude Desktop and verify the file path.

## Updating the skill

To pull the latest version:

```bash
# macOS
curl -o ~/Library/Application\ Support/Claude/skills/qa-passes/SKILL.md \
  https://raw.githubusercontent.com/sean-roth/phonebooth/main/docs/skills/qa-passes/SKILL.md

# Linux
curl -o ~/.config/Claude/skills/qa-passes/SKILL.md \
  https://raw.githubusercontent.com/sean-roth/phonebooth/main/docs/skills/qa-passes/SKILL.md
```

Restart Claude Desktop after updating.

## Using the skill

Trigger phrases:

- "Run a QA pass"
- "Audit this"
- "Sanity check before I [hand off / ship / commit]"
- "Look for [drift / inconsistencies / dead code / problems]"
- "Run a [consistency / traceability / etc.] pass"

Specific pass invocations:

- "Run a consistency pass" — for finding where files disagree
- "Run a traceability pass" — for ensuring changes propagated
- "Run a dead-code pass" — for finding stale references
- "Run a drift pass" — for finding scope/complexity creep
- "Run an assumption-check pass" — for finding unverified claims
- "Run a quality-gate pass" — for finding latent output-quality issues
- "Run a legal-and-ethical pass" — for finding regulatory exposure

For pre-handoff work, the skill recommends chaining: consistency → traceability → assumption-check → dead-code.

For post-pivot cleanup: dead-code → consistency → traceability.

For going live: legal/ethical → quality-gate → assumption-check.

## When to use it

Use after major architectural changes (like the spec 11 pivot in the phonebooth project), before handing work to another Claude or human, before going live, or whenever you have the feeling something might be off but can't pinpoint it.

If the request is vague ("just look it over"), the skill will ask which pass type(s) to run rather than producing a generic scan. That's the heart of the design — vague prompts produce vague review; named passes produce specific findings.

## Troubleshooting

**Skill doesn't trigger:** check that the SKILL.md is in the right folder for your OS. The frontmatter `name:` field needs to be unique across your installed skills — if there's a collision, rename one.

**Skill triggers but produces shallow output:** verify the SKILL.md isn't truncated. The full file is ~11KB. If your copy is much shorter, re-download.

**Claude runs all seven passes when one was asked for:** this is an anti-pattern the skill warns against. If it happens, tell Claude "just run the [specific] pass you were asked for" — the skill will recalibrate.

**Findings feel impressionistic rather than systematic:** the skill includes search heuristics for each pass type. If Claude isn't using them, ask: "What heuristic are you using for this pass?" That should refocus it.
