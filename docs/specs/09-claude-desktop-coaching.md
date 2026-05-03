# 09 — Claude Desktop Coaching Workflow (Discovery Calls)

## Purpose of this document

How Sean uses Claude Desktop with filesystem MCP to coach himself on discovery calls (not cold calls).

**Note: this spec was rewritten by spec 11 (recording pivot).** Earlier drafts described coaching cold-call transcripts produced by the dashboard's Whisper pipeline. That pipeline was removed; coaching now applies to discovery-call transcripts from Google Meet.

## The flow

```
Sean books a discovery call from a cold call
  ↓
Schedule Google Meet with the lead via email
  ↓
Discovery call happens in Google Meet (~30 minutes)
  - Google Meet shows recording indicator to all participants
  - This constitutes notice + implied consent under Illinois law
  ↓
After call ends, Sean downloads or copies the transcript
  - Google Workspace generates transcripts natively
  - Or use Otter.ai / similar third-party if Workspace doesn't
  ↓
Sean saves transcript as:
  storage/app/coaching/discoveries/{lead-name}-{date}.md
  ↓
Sean opens Claude Desktop, "Phonebooth Coaching" project
  ↓
"Coach my latest discovery call"
  ↓
Claude Desktop, via filesystem MCP:
  - Lists discoveries/ for files without matching feedback/
  - Reads the transcript
  - Reads the chosen sales framework skill from docs/skills/
  - Generates coaching markdown
  - Writes to feedback/{same-filename}.md
  ↓
Sean reads the feedback, refines for next call
```

## One-time setup

### 1. Configure filesystem MCP in Claude Desktop

Filesystem MCP is one of the standard MCP servers.

Claude Desktop config file location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Add (or merge into) the `mcpServers` section:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/phonebooth/storage/app/coaching",
        "/path/to/phonebooth/docs/skills"
      ]
    }
  }
}
```

The two arguments after the package name are the directories Claude Desktop is allowed to read and write within. Adjust paths to match Sean's OptiPlex setup.

**Why these two paths:**
- `coaching/` — Claude reads `discoveries/`, writes `feedback/`
- `docs/skills/` — Claude reads framework prompts (Jeb Blount, SPIN, etc.)

**Verify before assuming this works:** the filesystem MCP package name and config format may have changed. Check current docs at https://modelcontextprotocol.io/ before assuming the above is right.

### 2. Create folder structure

```bash
mkdir -p storage/app/coaching/discoveries
mkdir -p storage/app/coaching/feedback
```

These directories may need to be created during build step 1; they're not the dashboard's responsibility (the dashboard doesn't write to them anymore — Sean does, manually, after each discovery call).

### 3. Create a Claude Desktop Project

In Claude Desktop, create a new Project called "Phonebooth Coaching."

**Project knowledge:**

- The contents of `docs/skills/01-jeb-blount.md` (or whichever framework you want for cold-call mechanics if you ever recover those)
- A discovery-call-focused framework — SPIN selling or Sandler are common choices, both are richer than Jeb Blount for the discovery-call format. Add as a separate file in `docs/skills/` (e.g., `02-spin.md`).
- A short workflow note (template below)

**Workflow note template:**

```
You are Sean's sales coach. He runs cold calls to small businesses in Chicago,
some of which convert to 30-minute discovery calls in Google Meet. He needs
feedback on those discovery calls against whichever framework is loaded.

When Sean asks you to coach calls:

1. Use the filesystem MCP to list files in
   /path/to/phonebooth/storage/app/coaching/discoveries/

2. For each transcript file, check if a corresponding feedback file exists in
   /path/to/phonebooth/storage/app/coaching/feedback/

3. For any discovery transcript without feedback, read it, read the relevant
   framework skill in this project, and generate coaching using the framework's
   structure.

4. Write the coaching markdown to
   /path/to/phonebooth/storage/app/coaching/feedback/{same-filename}.md

5. Output the markdown directly with no preamble.

If Sean asks specific questions about a discovery call ("what did I miss in
the X conversation?"), read just that transcript and answer conversationally
without writing a feedback file. Save the file only when explicitly coaching.

If Sean wants pattern recognition across multiple discovery calls (e.g.,
"what objections keep coming up across these five calls?"), read the relevant
transcripts and respond conversationally.
```

### 4. Test the setup

In a Claude Desktop conversation in the Project:

1. Save a test transcript to `storage/app/coaching/discoveries/test.md` with some sample dialogue
2. Ask Claude: "Can you list the discoveries folder?" — should return the file via filesystem MCP
3. Ask: "Coach the test discovery call" — should generate coaching, write feedback file
4. Open `storage/app/coaching/feedback/test.md` — confirm the markdown is there
5. Delete the test files when satisfied

If any step fails, debug filesystem MCP setup before proceeding.

## Daily/per-session usage

After a discovery call:

1. End the Google Meet
2. Wait for Workspace to process the transcript (usually 5-15 minutes; Workspace emails it)
3. Or download the transcript directly from the Meet recording
4. Save as `storage/app/coaching/discoveries/{lead-name}-{date}.md`
   - Example: `storage/app/coaching/discoveries/acme-plumbing-2026-05-08.md`
   - Add a frontmatter section with lead name, date, your goal for the call, what disposition you'd give it
5. Open Claude Desktop, navigate to Phonebooth Coaching project
6. Start a new conversation
7. Say: "Coach my latest discovery call"
8. Read the feedback (it's saved to `feedback/{same-filename}.md`)

You can also do per-call review:

- "Read the Acme Plumbing call and tell me what stood out"
- "Coach the calls from this week and write feedback files"
- "Looking at my last 5 discovery calls, what's the recurring pattern in how I'm framing pricing?"

## What Claude Desktop has that the API didn't

The shift to Claude Desktop unlocks capabilities that one-shot API calls didn't:

- **Memory across conversation:** ask follow-up questions on a specific call
- **Pattern recognition across calls:** "across these 10 transcripts, what's the recurring weakness?"
- **Refinement:** "re-read the X call, I think you missed the moment at 12:30, look again"
- **Skill iteration:** Sean can refine the framework skill in real-time and Claude applies the new version
- **Cross-project context:** Claude Desktop's Memory across all of Sean's projects (Clara, SOPs Nobody Reads) means broader pattern recognition is possible

## Frontmatter template for transcripts

When saving a Google Meet transcript, add a frontmatter section:

```markdown
---
lead: Acme Plumbing
contact: Bob Acme
date: 2026-05-08
duration_minutes: 32
goal: qualify them, understand their AI use cases, propose pilot scope
disposition: pilot_proposed  # or whatever fits
---

# Discovery Call: Acme Plumbing — 2026-05-08

[transcript content here, exported from Google Meet]
```

The frontmatter helps Claude Desktop give context-aware coaching ("did Sean accomplish his stated goal?").

## Costs

$0 incremental. Sean has a Claude Pro/Max subscription. All usage stays within that.

## Common gotchas

- **Filesystem MCP path scoping:** Claude can only read/write within the directories listed in the config. If you try to access files outside, it'll fail.
- **Path differences across OSes:** the example paths are Linux-style. Adjust separators on macOS/Windows.
- **Project knowledge size limits:** the Jeb Blount skill is ~7KB which is fine. If skills grow, watch the project knowledge limit.
- **Concurrent edits:** if Sean is editing the skill file while Claude Desktop is reading it, the read might catch a partial state. Save fully before invoking coaching.
- **MCP startup:** filesystem MCP needs to start when Claude Desktop launches. If you change the config, restart Claude Desktop.
- **Google Meet transcript availability:** Workspace transcripts are a paid Workspace feature. Free Gmail accounts can't natively transcribe Meet recordings — Sean will need to use a third-party tool like Otter.ai (free tier available) or transcribe manually.

## What to do if filesystem MCP isn't available

Fallback workflow without MCP:

1. Sean opens transcript file in his editor
2. Copies content
3. Pastes into Claude Desktop conversation
4. Asks "coach this discovery call against the SPIN framework"
5. Claude responds with markdown
6. Sean copies the response, saves it as `feedback/{filename}.md` manually

More friction but works.

## Future enhancements (Phase 2+)

- **Auto-import from Google Meet:** a watcher process pulls transcripts from Google Drive when they're posted
- **Per-call framework selection:** Sean tells Claude which framework to use ("coach with Sandler" vs "coach with SPIN")
- **Discovery call records in DB:** Phase 1 keeps these as filesystem-only; Phase 2 might add a discovery_calls table linked to leads
- **Pattern reports:** weekly cron job invokes Claude Desktop to summarize the week's discovery calls
- **Pre-discovery brief generation:** Claude reads the cold-call notes for a lead and generates a discovery-call brief before the call
- **Cold-call coaching reintroduction:** if field testing shows cold-call coaching would have been valuable, the Whisper pipeline (in git history) can be restored

These are all roadmap. Phase 1 stays focused on the discovery-call coaching loop because that's where the value is.
