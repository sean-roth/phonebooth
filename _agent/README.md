# _agent — SOPs Nobody Reads sales system

The automation that feeds the human work of selling. It sources Midwest
manufacturers to call and, over time, will help manage the funnel behind them.

**Prime directive: this system exists to put Sean on the phone more — not to
become a bigger thing to build instead of calling.** Every layer earns its
place by removing friction from the human work. See `ROADMAP.md` before adding
anything.

## The why
Bring modern onboarding to Midwest manufacturers — the industrial heartland
Sean is from — starting with the Chicago and Detroit metros. We take a shop's
own procedures and turn them into training a new hire works through on a
device, with a trainer checking understanding. This folder keeps the call
pipeline full so the selling can happen.

## Territory
Chicago metro first, then Detroit metro — months of runway. Everything is
dialed from a single Chicago number (Mint), which reads as a coherent regional
business call across the whole Midwest. The wider region (Milwaukee, Grand
Rapids, Cleveland, Akron, Rockford, Fort Wayne, Toledo, Columbus, Cincinnati,
Indianapolis) is the long-term well — added to the sweep only when Chicago and
Detroit genuinely thin.

## The target (short version)
Privately-held manufacturers, ~50–200 employees, with a real production floor:
metal fabrication, machining/CNC, screw machining, tool & die, stamping,
injection molding/plastics, springs & wire forming, precision grinding, food
processing/packaging, industrial finishing. Owner- or family-run, single
location. The full governing rules live in `docs/sales/lead-generation-guide.md`
— that guide is the source of truth; this folder operationalizes it.

NOT: national branch plants, distributors/wholesalers, chemical/pharma/bio
(high-regulation), machinery dealers, or auto/consumer shops.

## Folder map
- `README.md` — this file
- `ROADMAP.md` — what gets built when. Read before adding anything.
- `skills/leads/` — the lead-gen skill (point a Claude Code agent here)
  - `SKILL.md` — entry point: workflow, tools, where the spreadsheets live
  - `qualification-prompt.md` — the Sonnet system prompt (ICP + exclusions +
    real keep/reject examples + H/M/L)
  - `sweep-matrix.md` — the metro × corridor × category queue
  - `output-format.md` — the tracker column format leads are written in
- `data/` — dedup database + CSV storage
  - `README.md`, `schema.sql`, `.gitignore`
- `strategy/` — context for sales-strategy conversations
  - `sales-strategy.md` — start new strategy chats from here

## Tools (via MCP in Claude Code)
- Google Maps (Places) — source manufacturers by area + category
- Firecrawl — verify web presence / size signals
- Twilio Lookup (or any number-validation API) — scrub dead numbers
- Google Drive — read/append the live call-tracker spreadsheets
- GitHub — this repo (source of truth for guide, prompts, matrix)

## What stays human, always
Calling. The review pile of ambiguous leads. Deciding when a metro is mined
out. Changing the guide. The agent sources and filters; it never decides who
is worth a call.

## Product facts (so any agent describes it right)
- What it is: a company's own procedures turned into slides a new hire clicks
  through on a device, then a trainer checks they understood it.
- Demo: a real module built from an OSHA lockout/tagout procedure
  (29 CFR 1910.147), at sopsnobodyreads.com/demo. A client's module is built
  from THEIR procedures.
- Price: $3,500 pilot, one module, delivered in ~one week.
- Voice: plain, short sentences (many owners speak English as a second
  language). Say "onboarding"/"module," never "training" (implies Sean teaches
  the staff). Never say AI, blockchain, SCORM, LMS, "compliance," "platform,"
  "solution."
- Identity: contact@sopsnobodyreads.com · sopsnobodyreads.com (never
  seanroth.ai in outreach).
