# 09 — Claude Desktop Coaching Workflow

## Purpose of this document

How Sean uses Claude Desktop (his existing subscription) to generate coaching feedback for each call, via filesystem MCP. Replaces the Claude API integration that was originally in spec 05.

This is a setup doc and a usage doc. The Engineer doesn't build any code from this — Claude Desktop is configured by Sean directly.

## The flow

```
Sean makes calls all morning
  ↓
Each Process Call writes:
  storage/coaching/transcripts/{call_id}.md
  ↓
Sean opens Claude Desktop (with phonebooth Project)
  ↓
"Coach my unprocessed calls"
  ↓
Claude Desktop, via filesystem MCP:
  - Lists transcripts/ for files without matching feedback/
  - Reads each transcript
  - Reads the Jeb Blount skill from docs/skills/
  - Generates coaching for each
  - Writes to feedback/{call_id}.md
  ↓
Sean opens dashboard
  ↓
Call detail pages now show coaching feedback
```

## One-time setup

### 1. Configure filesystem MCP in Claude Desktop

Filesystem MCP is one of the standard MCP servers. If it's not already configured in Claude Desktop, add it.

The Claude Desktop config file location depends on OS:
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
- `coaching/` — Claude reads `transcripts/`, writes `feedback/`
- `docs/skills/` — Claude reads the framework prompts (Jeb Blount, etc.)

**Verify before assuming this works:** the filesystem MCP package name and config format may have changed. Check current docs at https://modelcontextprotocol.io/ before assuming the above is right.

### 2. Create a Claude Desktop Project

In Claude Desktop, create a new Project called "Phonebooth Coaching". Projects let you set persistent context across conversations.

**Project knowledge** (paste these in or link as files):

- The contents of `docs/skills/01-jeb-blount.md` — the framework Claude coaches against
- A short workflow note (see template below)

**Workflow note template** to paste into the project:

```
You are Sean's sales coach. He runs cold calls to small businesses in Chicago and
needs feedback against the Jeb Blount framework loaded in this project.

When Sean asks you to coach calls:

1. Use the filesystem MCP to list files in
   /path/to/phonebooth/storage/app/coaching/transcripts/

2. For each transcript file, check if a corresponding file exists in
   /path/to/phonebooth/storage/app/coaching/feedback/

3. For any transcript without feedback, read the transcript, read the
   Jeb Blount skill in this project, and generate coaching using the
   exact output structure the skill specifies.

4. Write the coaching markdown to
   /path/to/phonebooth/storage/app/coaching/feedback/{call_id}.md
   where {call_id} matches the transcript's call_id from the frontmatter.

5. Output the markdown directly with no preamble — start with the
   first heading. Sean's dashboard will render this as-is.

If Sean asks specific questions about a call ("what did I do wrong on call 15?"),
read just that transcript and answer conversationally without writing a feedback
file. Save the file only when explicitly coaching.
```

This becomes the system prompt that runs every conversation in this Project.

### 3. Test the setup

In a Claude Desktop conversation in the Project:

1. "Can you list the transcripts folder?" — should return file list via filesystem MCP
2. "Can you read transcript 1 if it exists?" — confirms read access
3. "Coach call 1" — should read transcript, generate coaching, write feedback file
4. Open `storage/app/coaching/feedback/1.md` — confirm the markdown is there
5. Open the dashboard, navigate to call detail page for call 1 — confirm coaching renders

If any step fails, debug filesystem MCP setup before proceeding.

## Daily/per-session usage

After a calling session (or per-call, your choice):

1. Open Claude Desktop, navigate to Phonebooth Coaching project
2. Start a new conversation
3. Say: "Coach my unprocessed calls"
4. Wait while Claude reads, generates, and writes (a few seconds per call)
5. Open dashboard, refresh call detail pages — coaching is there

You can also do per-call review:

- "Read call 15 and tell me what stood out" — conversational, no file written
- "Coach calls 14, 15, 16 and write feedback files" — batch mode
- "Looking at the last 10 calls, what patterns are you seeing?" — meta-analysis, no file written

## What Claude Desktop has that the API didn't

The shift to Claude Desktop unlocks capabilities that one-shot API calls didn't have:

- **Memory across conversation:** ask follow-up questions on a specific call without restating context
- **Pattern recognition across calls:** "across these 10 transcripts, what's the recurring weakness?"
- **Refinement:** "re-read call 15 — I think you missed the moment at 03:14, look again"
- **Skill iteration:** "this coaching feels generic, can we adjust the framework?" — Sean can refine the skill in real-time and Claude will apply the new version
- **Connection to other knowledge:** Claude Desktop's Memory across all of Sean's projects (Clara, SOPs Nobody Reads) means broader pattern-recognition is possible

## Costs

$0 incremental. Sean has a Claude Pro/Max subscription. All usage stays within that.

## Common gotchas

- **Filesystem MCP path scoping:** Claude can only read/write within the directories listed in the config. If you try to access files outside, it'll fail silently or with permission errors. Make sure the coaching folder is in scope.
- **Path differences across OSes:** the example paths are Linux-style. On macOS or Windows, adjust separators. The Engineer/Sean must use real paths matching the OptiPlex.
- **Project knowledge size limits:** the Jeb Blount skill is ~7KB which is fine. If skills grow, watch the project knowledge limit.
- **Concurrent edits:** if Sean is editing the skill file while Claude Desktop is reading it, the read might catch a partial state. Save fully before invoking coaching.
- **MCP startup:** filesystem MCP needs to start when Claude Desktop launches. If you change the config, restart Claude Desktop.

## What to do if filesystem MCP isn't available

Fallback workflow without MCP:

1. Sean opens transcript file in his editor
2. Copies content
3. Pastes into Claude Desktop conversation
4. Asks "coach this call against the Jeb Blount framework"
5. Claude responds with markdown
6. Sean copies the response, saves it as `feedback/{call_id}.md` manually

This is more friction but works. Spec 05's pipeline still produces transcript files; Claude Desktop is just used as a regular chat instead of via MCP. Sean can use this pattern Monday if MCP setup isn't done yet, then upgrade to MCP later.

## Future enhancements (Phase 2+)

- **Auto-coach on transcribe:** a watcher process invokes Claude Desktop CLI (if available) to auto-trigger coaching when a new transcript appears
- **Per-call skill selection:** Sean tells Claude Desktop which framework to use ("coach call 15 with Sandler") — multiple skills loaded as project knowledge
- **Pattern reports:** weekly cron job invokes Claude Desktop to summarize the week's calls
- **Claude Desktop reading the SQLite directly:** instead of file-based, Claude reads from the database via SQLite MCP — but this is more setup with no clear benefit over files
- **Pain-points themes report:** dedicated skill that analyzes pain_points fields across all calls for product-discovery patterns

These are all roadmap. The Phase 1 setup above is enough to get value Monday morning.
