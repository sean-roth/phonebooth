# DESIGN.md — SOPs Nobody Reads

Single-file brand reference for AI assistants working on the SOPs Nobody Reads site, modules, or any other brand surface. This document consolidates the brand foundations, palette, typography, copy, imagery direction, and production specifications into one place.

When this file is loaded, the AI has everything needed to make brand-consistent decisions during a build, refactor, or new-surface creation. For deeper rationale on any specific decision, see the individual files in this directory.

---

## What this brand is, in one paragraph

SOPs Nobody Reads is a small instructional design practice run by Sean Roth. The practice takes a company's own written procedures and converts them into interactive training modules that crews actually finish. The brand serves people who make, move, or maintain the physical civilization around us — trade contractors, property managers, warehouses, manufacturers. The brand is in service to other people's craft — never claiming it, never imitating it, always supporting it. The phrase that captures the brand's posture: **aiding in craftsmanship.**

---

## The market

**Active segments:**
- Trade contractors (primary focus, Chicago, active cold-call pipeline)
- Property managers (operations side only — maintenance, not leasing)
- Warehouses (initial focus is Taiwanese-American operators)
- Manufacturers (slower sales cycle, broad segment)

**Explicit exclusions:**
- Medical (regulatory liability)
- Financial services (regulatory liability)
- Security and defense (regulatory liability)
- Trucking (catastrophic-tail liability, subscale economics)
- Restaurants and retail (low budget, low stakes)
- Knowledge workers / office training (different category — corporate L&D market)

The boundary: **physical work with conventional liability.**

---

## Palette (committed)

| Role | Hex | Color name |
|------|-----|-----------|
| Primary ink | `#1f3a2e` | Deep forest green |
| Background | `#f4ede0` | Warm cream |
| Accent | `#3a1f2e` | Dark aubergine |
| Utility | `#6b5d4a` | Warm gray |

**Accessibility:** All combinations pass WCAG AA. Forest green and aubergine on cream both exceed 7:1 (AAA). Warm gray on cream is 5.48:1 (AA for body text).

**Usage rules:**
- Forest green dominates: type, primary graphics, wordmark
- Cream is the background everywhere; never pure white, never alternate section colors
- Aubergine appears sparingly (2-3 times per page max): links, primary CTAs, section dividers
- Warm gray is for utility text only: captions, footers, fine print
- Color should never be the only signal for meaning — links must be underlined as well as colored

**Watch-points:**
- Forest green has association with landscaping; mitigated through context (editorial typography, conceptual imagery, copy about training). Hold the palette unless feedback consistently surfaces the landscaping read.

**Future tonal variations (not committed, added if a real need surfaces during build):**
- Light forest green (~`#a8b8a4`) for hover states, soft backgrounds, subtle borders

---

## Typography (committed)

| Role | Typeface | Source |
|------|----------|--------|
| Display + Body | Lora | Google Fonts |
| Utility | IBM Plex Sans | Google Fonts |

**Weights to load:**
- Lora 400 (regular), 500 or 600 (headlines), 400 italic
- IBM Plex Sans 400

**Production tuning (defer to actual rendering):**
- Exact headline weight (500 vs 600)
- Letter-spacing for headlines (likely -0.3 to -0.5px at large sizes)
- Mobile body size (16 or 17px)
- Whether utility sans stays IBM Plex or swaps to Inter

**Starting type scale:**

Desktop:
- H1: 38-42px, Lora Medium/SemiBold
- H2: 26-32px, Lora Medium
- H3: 20-22px, Lora Medium or Italic
- Body: 16-17px, Lora Regular, line-height 1.6-1.7
- Utility: 12-13px, IBM Plex Sans Regular

Mobile:
- H1: 30-34px
- H2: 22-26px
- H3: 18-20px
- Body: 16px (don't go smaller)
- Utility: 12px

**Fallback stack:**
```css
font-family: 'Lora', Georgia, 'Times New Roman', serif;
font-family: 'IBM Plex Sans', system-ui, sans-serif;
```

Use `font-display: swap` for both.

---

## Homepage copy (committed)

### Hero

> # Custom training, made for how the work actually happens.
> ### Built from your team's existing documentation.

### Section 2 — *The materials exist. They go unused.*

> Every shop has procedures written down somewhere. The PDF on the office computer. The binder in the truck. The safety manual the consultant produced two years ago. The documents are real, and the knowledge in them is real, but a forty-page file on a phone between jobs reaches no one. The information might as well not exist.
>
> Training has a delivery problem more often than it has a content problem.

### Section 3 — *The real question*

> ## The real question is whether the crew actually knows.
>
> A signed acknowledgment is paperwork. A completed slideshow is a click trail. Neither one is evidence that anything was understood.
>
> What companies pay for, when they pay for training, is comprehension. Everything else is documentation of an event that may or may not have happened in a person's head.

### Section 4 — *What the work is*

> ## What the work is.
>
> I'm Sean. SOPs Nobody Reads is a small practice built around a specific kind of translation: rendering a company's written procedures into training the crew will actually finish.
>
> The content stays the shop's — same procedures, same expertise, same authorship. What changes is the form. Visual where the original was dense, sequenced where it was a wall of text, tested where it assumed comprehension. The process is collaborative, because the owner is the only one who knows whether the translation is faithful to how the work actually gets done.

### Section 5 — *The process*

> ## The process
>
> **Documents in.** The shop sends what it has, in whatever format. PDFs, Word files, scans, exports from existing systems.
>
> **Translation.** I convert the material into an interactive course — narrated, visual, sequenced, with comprehension checks. About a week per topic. Drafts shared as the work progresses, owner sign-off before the course reaches the crew.
>
> **Course out.** A 30-to-45-minute training module that runs on any device with a browser. The crew completes it on their own time. Completions are tracked.

### Section 6 — *What it costs*

> ## What it costs
>
> **Pilot module — $3,500.** One topic. A real proof of concept.
>
> **Onboarding starter — $14,000 to $18,000.** Four topics, covering what a new hire needs in the first month.
>
> **Full program — $32,000 to $42,000.** Everything the shop trains people on, sequenced and built out. OSHA topics included where the shop's work requires them.
>
> Hosting runs $200 to $400 a month, optional — if a shop has its own system, I can deliver files that work with it.

### Section 7 — *A demo*

> ## A demo
>
> Ten minutes, a real module built from a real contractor's procedures. The clearest way to see what the work looks like.
>
> *Open the demo →*

### Section 8 — *A short call*

> ## A short call
>
> Four questions about how the shop onboards now and where the gaps are. If the practice is a fit, I'll say so. If it isn't, I'll say that too.
>
> *Book the call →*

### Footer

> Sean Roth. Instructional designer working with Chicago-area trade contractors.
>
> The work is rendering. The shop owns the expertise. I make sure the crew can actually use it.
>
> sean@seanroth.ai

---

## Site structure

The homepage sells the brand. Segment pages sell the segment-specific use case.

**Top navigation:** Includes a "Who is this for" dropdown linking to:
- `/for/contractors`
- `/for/property-managers`
- `/for/warehouses`
- `/for/manufacturers`

**URL convention:** `/for/[segment]` — the *for* prefix is intentional, signaling that each page serves a specific audience rather than describing them.

---

## Segment page architecture (consistent across all four)

Three sections:

1. **Hero** — segment-specific headline naming the operational reality, with a quieter subtitle naming the training as the answer. Primary CTA above the fold. Scroll cue inviting the curious visitor to keep going.

2. **Story** — three scenes, each with a non-figurative illustration and a short blurb. Narrative arc: setup, intervention, outcome. The story shows what the training looks like in use without claiming or pitching.

3. **Closing** — a brief restatement of what's in the deliverable, plus a final CTA.

**Pronoun convention:** All segment pages use *he* for hypothetical workers. The brand's market sectors have outsized male representation.

**Language calibration by segment:**
- Contractor: vernacular allowed (*losing daylight*)
- Property manager: plain language with brand voice in signature phrases (*being a guest in someone's home*)
- Warehouse: maximally plain language (non-native English readership)
- Manufacturer: plain and direct throughout

---

## Segment page copy (committed)

### Contractor page (/for/contractors)

**Hero:**
> # Your best worker is losing daylight to repeat questions.
> ### Custom training that lets the new hire find out what he doesn't know.

**Scene 1:** Your best worker is on his fourth job of the day. The new hire is shadowing him. Every fifteen minutes there's another question — sometimes about something the new hire should have picked up two jobs ago.

**Scene 2:** The new hire pulls up the training on a tablet. Ninety seconds on the procedure he's about to try. He sees the steps, the specific equipment your shop uses, what to watch for, what goes wrong when it goes wrong.

**Scene 3:** Now his questions are different. He's not asking what to do — he knows what to do. He's asking *why this fitting goes in first* or *what does it look like when it's wrong.* Your best worker gets to teach the part that requires him.

**Closing:** Modules built from your shop's procedures and the equipment your crews actually use.

### Property manager page (/for/property-managers)

**Scope:** Operations side only — maintenance, vendor coordination, tenant interactions during service work. Not leasing.

**Hero:**
> # The technical work is what your staff knows. The human work is what your tenants remember.
> ### Custom training that gets both right.

**Scene 1:** A tenant called this morning. The dishwasher is leaking. Your maintenance worker is heading there now. He has walked into 200 apartments this year — but this is the first time he has been in this one, and the tenant doesn't know him.

**Scene 2:** Before he knocks, he pulls up the procedure on his phone. The dishwasher model, the shutoff location, the common failure points. He also reviews how to handle the tenant interaction — what to say at the door, what to ask before working, what to leave when he is done. Two minutes.

**Scene 3:** He fixes the appliance. But he also introduces himself, asks before moving anything, explains what went wrong, cleans up after himself, and tells the tenant what to watch for. The leak is gone. The tenant is calmer than when he arrived. The training did that.

**Closing:** Modules built from your buildings, your appliances, your procedures — and what your maintenance staff needs to know about being a guest in someone's home.

### Warehouse page (/for/warehouses)

**Hero:**
> # Your new hires need to be accurate from day one.
> ### Custom training that teaches what experienced workers already know.

**Scene 1:** Wednesday morning. Your lead is on a different floor handling a vendor problem. A new worker is on the line. He pulled the wrong item twice this hour and didn't notice. The cartons are already on the truck.

**Scene 2:** He opens the training before his shift. The two items he keeps confusing are shown side by side: what they look like, where they are stored, what the labels say, what to check before scanning. Three minutes.

**Scene 3:** Now he sees the difference. His speed catches up to the experienced workers within a week instead of a month. Errors get caught before the customer sees them. Your lead handles the vendor problem without worrying about the floor.

**Closing:** Modules built from your warehouse's actual items, racking layout, scanner steps, and daily procedures.

### Manufacturer page (/for/manufacturers)

**Hero:**
> # Train your new hires the same way every time.
> ### Custom training that doesn't change with whoever does the teaching.

**Scene 1:** Your shift lead trained the experienced operator. That operator is training the new hire this week. By the time the procedure reaches him, three small details have changed and nobody remembers why.

**Scene 2:** We capture the procedure correctly — what it looks like when it's right, what the common mistakes are, what the judgment calls require. The training becomes the standard. Everyone runs through the same version.

**Scene 3:** Now your new hire is learning the procedure the same way your senior operator did. When he trains the next new hire, it stays the same. The drift stops. The standard is the standard.

**Closing:** Modules built from your equipment, your procedures, and the knowledge your senior operators have built over years on your floor.

---

## Imagery direction

**All imagery is non-figurative.** No people, no figures, no workplace scenes.

**Style reference:** Christoph Niemann (New Yorker covers, Sunday Sketches). Reductive conceptual illustration. Single conceptual relationship per image. Minimum elements needed to land the idea.

**Properties to maintain:**
1. Reductive composition — often two or three shapes total
2. Flat graphic shapes — no photorealism, no detailed textures
3. Restricted internal palette — no more than two or three colors, drawn from brand palette
4. Conceptual punch — one idea that clicks when the viewer understands it
5. Editorial restraint — never competes with the text

**Reference territory to draw from:**
- Editorial design (NYT longform, n+1, The Atlantic, Phaidon, NYRB Classics)
- Technical reference (McMaster-Carr, Caterpillar service manuals, military field manuals)
- Field guides (Peterson, Audubon)
- Museum and archival design
- Sequential art and reductive conceptual illustration

**Reference territory to AVOID:**
- Safety/compliance category visual language (ClickSafety, Vector, Avetta)
- Construction-site cues (hi-vis, hardhats, jobsite photography)
- Warehouse-floor stock photography
- SaaS chrome (gradients, isometric illustrations, friendly mascots)
- Tech-startup minimalism
- Craftsman-tool imagery (verges on self-indulgent; also edges toward exclusion of customers whose specific craft isn't depicted)

**Production:** AI image generation (Seedream 4.5 on Replicate). Most generations will be rejected. Discipline of rejection is what creates a consistent visual library rather than a stream of AI outputs.

**Visual vocabulary across segment pages:**
- Scene 1: state of disorder, tangle, drift (the problem)
- Scene 2: rectangular shape with structured marks (the training intervention)
- Scene 3: resolved or coherent state (the same elements from Scene 1 now in order)

The recurring "rectangular form with structured marks" in Scene 2 of every segment page becomes a visual signature for *the training itself.*

**For specific generation-ready prompts, see `image-prompts.md`.**

---

## The cosplay test

The single most important test the brand has to pass: **does this visual / word / image suggest I'm trying to be the customer?**

If yes — kill it. Hi-vis accents. Hardhat photography. Carhartts in the founder photo. Jobsite stock imagery. Warehouse-floor stock photography. "We've worked in the field" language. Anything that implies the brand is from any of the trades or industries it serves.

The trades respect *other craft*. They don't respect imitation of their craft. The brand's dignity comes from being clearly itself — editorial, transmission-oriented, considered — in service to the customer's craft. Like a luthier. Like a scribe. Like a cartographer.

This test applies equally across all segments: the brand should not cosplay as a contractor, as a warehouse manager, as a property manager, or as a manufacturer.

---

## Brand voice

Direct. Confessional. Specific. Names triggers and pain by their real names. Comfortable with uncomfortable claims. Doesn't soft-sell. Doesn't perform earnestness.

**Voice rules:**
- Use the customer's own vocabulary (*best worker* not *journeyman*, *losing daylight* not *productivity loss*)
- Observational over instructional (the brand describes what happens, doesn't tell the customer what to do)
- Plain language is the default; segment-specific calibration is the optimization
- Avoid AI tells: forced negation (*Not X. Y.* construction), three adjectives in a row, false parallelism, *we believe* corporate-speak

**Phrases that carry brand weight and should not be paraphrased:**
- "Aiding in craftsmanship" (brand posture, internal only)
- "Custom training, made for how the work actually happens" (homepage hero)
- "Built from your team's existing documentation" (homepage subhead)
- "Being a guest in someone's home" (property manager signature)
- "The work is rendering" (footer; describes what the practice does)

---

## Wedge: Onboarding

Every operation in the brand's market onboards new hires. The pain is universal. "Onboarding" as a word is novel in the safety-training cold-call context — slips past the *here comes another vendor about safety training* shutdown. The first module sold establishes the relationship; subsequent modules build the institutional reference.

**Orienting question for any engagement:** *What does a new employee need to know first, second, and so on?*

---

## What's deferred (not committed)

These are production decisions to make during build, not architectural questions to revisit:

- Exact font weights for headlines (500 vs 600)
- Letter-spacing tuning
- Mobile body text size (16 vs 17px)
- Whether utility sans stays IBM Plex or swaps to Inter
- Imagery — to be generated iteratively, starting with the four homepage images and twelve segment page images (16 total, see `image-prompts.md`)
- Logo / wordmark — likely just "SOPs Nobody Reads" set in Lora with deliberate proportions; no separate mark needed
- Application beyond the homepage and segment pages — module player UI, email signature, invoice template, proposal template

These are deferred to *production*, not abandoned. When the build encounters a need, decide deliberately and update this document.

---

## What's outside the brand entirely

If the AI encounters a request that conflicts with these, treat it as drift to flag:

- Hi-vis safety yellow or orange anywhere in the visual identity
- Stock photography of any workplace
- People depicted in any imagery (figurative or otherwise)
- Use of the term "compliance" as positioning (it's a capability the practice serves, not the value proposition)
- AI or blockchain or "platform" language in customer-facing copy
- Promises about regulatory expertise (the brand explicitly disclaims this)
- Generic "we help businesses..." corporate language
- Three-adjective constructions ("modern, scalable, intuitive")
- Forced negation patterns

---

## Quick lookup index

**Need the palette?** Section "Palette (committed)"
**Need the typography?** Section "Typography (committed)"
**Need the homepage copy?** Section "Homepage copy (committed)"
**Need a specific segment page?** Section "Segment page copy (committed)"
**Need imagery direction?** Section "Imagery direction" (and `image-prompts.md` for actual prompts)
**Need to check if something is on-brand?** Sections "The cosplay test," "Brand voice," "What's outside the brand entirely"
**Need to understand why a choice was made?** See individual files in this directory; each one has rationale notes.

---

## Repository structure

Other files in this directory provide deeper rationale:

- `brand-foundations.md` — the layered model (essence, promise, market, worldview, character, voice, etc.)
- `palette.md` — palette decisions with full rationale and watch-points
- `typography.md` — typography decisions with full rationale
- `homepage-copy.md` — homepage with section-by-section notes
- `segment-pages.md` — segment pages with architectural notes and segment-specific tone discussion
- `image-prompts.md` — 16 generation-ready prompts with notes
- `designer-brief.md` — synthesis for human designers
- `cold-call-pitch.md` — sales script (contractor-scoped)
- `discovery-questions.md` — 15-minute call structure (contractor-scoped)

DESIGN.md (this file) consolidates what an AI needs for fast lookup. The other files preserve the reasoning that produced each decision.
