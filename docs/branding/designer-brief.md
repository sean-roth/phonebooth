# Designer Brief — SOPs Nobody Reads

A single document for the designer working on the SOPs Nobody Reads visual identity. Synthesizes the brand foundations, palette, typography, and homepage into a working brief. The other files in this folder (brand-foundations.md, palette.md, typography.md, homepage-copy.md, cold-call-pitch.md, discovery-questions.md) provide deeper rationale where needed.

---

## What the brand is

SOPs Nobody Reads is a small instructional design practice run by Sean Roth. The practice takes a company's own written procedures — SOPs, safety manuals, equipment documentation — and converts them into interactive training modules that crews actually finish.

The brand's market is **people who make, move, or maintain the physical civilization around us.** Operations where the work happens in the physical world, where competence has to actually transfer from one person to another, where procedures govern real-world consequences.

**Current segments:** trade contractors (primary, Chicago focus), property managers, warehouses, manufacturers.

**Excluded segments:** medical, financial, security, trucking, restaurants, retail, and knowledge workers / office training. These exclusions are either liability-driven (medical, financial, security create conversion liability the practice can't absorb), economics-driven (restaurants and retail have low budgets relative to value delivered; trucking is subscale and high-tail-liability), or category-driven (knowledge workers are a different category entirely — corporate L&D is a competitor's market, not ours).

The brand essence: **tribal knowledge deserves to be transmitted.** Craft has lineage. The physical world is older than digital technology and will outlive it. Domain knowledge cannot be generated; it can only be transmitted. The practice exists to make that transmission work.

The closest professional analog for the brand's character: **a luthier.** Builds the instrument that lets the musician's craft be heard. Doesn't write the music. Doesn't play the music. Is a master of his own craft precisely because he knows he is not the musician. The luthier has no cosplay risk because his identity is built on the clear distinction between his work and the musician's.

The brand's working phrase for its own posture: **aiding in craftsmanship.**

## What the brand is not

The brand explicitly rejects:

- **The safety/compliance category aesthetic.** No hi-vis yellow or orange. No hardhat imagery. No jobsite stock photography. No warehouse-floor stock photography. No construction-site visual cues of any kind. The brand is in service to its customers, not from them.
- **Tech-vendor aesthetics.** No gradients, no abstract isometric illustrations, no friendly mascots, no startup minimalism. The brand is not a SaaS product.
- **Performance of authenticity.** No rustic costume aesthetics. No vintage typography as cosplay. No Field Notes-style craft heritage performance.
- **Self-decoration.** Design that draws attention to itself is design that has failed. The visual identity supports the message and the customer journey, playing second to both.

## The cosplay test

The single most important test the visual identity must pass: **does this visual / word / image suggest the brand is trying to be the customer?**

If yes — kill it. The brand should not cosplay as a contractor, as a warehouse manager, as a property manager, or as a manufacturer. The customer's industries respect *other craft*. They don't respect imitation of their craft. The brand's dignity comes from being clearly itself — editorial, transmission-oriented, considered — in service to the customer's craft. Like a luthier. Like a scribe. Like a cartographer.

## Reference territory

The visual identity should draw from:

- **Editorial design** — serious nonfiction publishing, Phaidon, NYRB Classics, longform editorial layouts
- **Reductive conceptual illustration** — Christoph Niemann is the closest single reference (his New Yorker covers and Sunday Sketches work). Single ideas made concrete through minimum elements.
- **Sequential art logic** — panel pairs, before/after compositions, visual transitions that show change between two states
- **Reference and archival aesthetics** — well-made technical references, museum design, vintage scientific illustration

The visual identity should avoid:

- Anything from the safety/compliance category (ClickSafety, Vector, Avetta visual language)
- Construction-site, warehouse-floor, or industrial-plant visual cues
- SaaS chrome
- Tech-startup minimalism

## Palette (committed)

| Role | Hex | Color |
|------|-----|-------|
| Primary ink | `#1f3a2e` | Deep cool forest green |
| Background | `#f4ede0` | Warm cream |
| Accent | `#3a1f2e` | Dark aubergine |
| Utility | `#6b5d4a` | Warm gray |

**Coolors reference:** https://coolors.co/1f3a2e-f4ede0-3a1f2e-6b5d4a

Accessibility verified: all combinations pass WCAG AA, most exceed AAA. Contrast comes from lightness differences rather than hue differences, making the palette robust for all color vision types.

Usage rules:
- Forest green dominates. Use for type, primary graphics, the wordmark.
- Cream is the background everywhere. Avoid pure white. Avoid alternate backgrounds for sections.
- Aubergine is sparing. No more than two or three appearances per page. Reserve for links, primary CTAs, section dividers.
- Warm gray is for utility text only.
- Color should never be the only signal for meaning (links must be underlined as well as colored).

Known watch-point: forest green has association with landscaping and outdoor brands. Mitigation is context — editorial typography, conceptual imagery, copy about training and procedures. If feedback consistently surfaces the landscaping read, revisit. Otherwise, hold the palette.

Future tonal variations may be needed for hover states, light backgrounds, or subtle borders — a light forest green (#a8b8a4 or similar) would be the natural extension. Add deliberately when a real need surfaces.

## Typography (committed)

| Role | Typeface | Source |
|------|----------|--------|
| Display + Body | Lora | Google Fonts |
| Utility | IBM Plex Sans | Google Fonts |

Lora is a free, open-source serif designed for sustained reading on screens. Sits in the workhorse-editorial register — close in feel to Tiempos but with slightly warmer, more humanist letterforms. Used for both display and body to keep the typographic system tight. Hierarchy is created through size and weight, not typeface change.

IBM Plex Sans handles utility text only (captions, footers, fine print). Same family used on seanroth.ai for continuity with the personal brand.

Starting size hierarchy (adjust in production):

**Desktop:**
- H1: 38-42px Lora Medium or SemiBold
- H2: 26-32px Lora Medium
- H3: 20-22px Lora Medium or Italic
- Body: 16-17px Lora Regular, line-height 1.6-1.7
- Utility: 12-13px IBM Plex Sans Regular

**Mobile:**
- H1: 30-34px
- H2: 22-26px
- H3: 18-20px
- Body: 16px (don't go smaller)
- Utility: 12px

Weights to use: Lora Regular (400), Lora Medium (500) or SemiBold (600) for headlines, Lora Italic (400) for emphasis. Bold (700) is probably too heavy for the brand's restrained register.

Production tuning decisions (defer to real implementation):
- Exact headline weight (500 vs 600)
- Letter-spacing for headlines (likely -0.3 to -0.5px at large sizes)
- Mobile body size (16 or 17px depending on screen density)
- Whether utility sans stays IBM Plex or swaps to Inter

## Imagery direction

Custom conceptual illustrations in the Niemann mode. Properties to maintain across all images:

1. **Reductive composition.** Minimum elements needed to land the idea. Often two or three shapes total. One conceptual relationship per image.
2. **Flat, graphic shapes.** No photorealistic rendering. No detailed textures. Reduced forms.
3. **Restricted internal palette.** Each image uses no more than two or three colors, drawn from or harmonizing with the brand palette where possible.
4. **Conceptual punch.** Each image carries a single idea that "clicks" when the viewer understands it. The image isn't decoration — it's another channel for the message.
5. **Editorial restraint.** The image should never compete with the text it accompanies. It exists to support and reinforce, not to be admired.

All imagery is produced through AI image generation (Seedream 4.5 on Replicate), then curated against these criteria. Most generated images will be rejected. The discipline of rejection is what creates a consistent visual system rather than a stream of AI outputs.

**No literal industry imagery.** No hardhats, no construction workers, no jobsite scenes, no forklifts, no warehouse aisles, no factory floors, no apartment buildings. The imagery transmits abstract ideas — transmission, comprehension, structure, translation, continuity across generations — not depictions of the customer's world.

**No craftsman-tool imagery either.** Earlier exploration tested antique tools (carpenter's plane, luthier's chisel) as hero imagery. This direction was rejected because (a) it edges toward exclusion — the visitor whose craft isn't depicted feels less recognized — and (b) it verges on self-indulgence — beautifully rendered tools draw attention to the brand's aesthetic sophistication rather than to the work the brand does. Heritage of craftsmanship should inform the imagery's restraint and care, not be the imagery's subject.

The imagery should be abstract enough to work for any of the brand's current segments (contractors, property managers, warehouses, manufacturers) without favoring or depicting any one of them.

## What the visual identity has to do

Six things, in priority order:

1. **Make the message land.** The brand voice is direct, confessional, specific. Visual choices must support that voice, not soften or decorate it.
2. **Establish dignity.** The visitor must feel he is encountering a serious practice, not a marketing site.
3. **Pass the cosplay test.** Nothing in the visual identity should suggest the brand is from any of the customer's industries.
4. **Read as old work in modern form.** The aesthetic should feel rooted — editorial, archival, considered — while being clearly contemporary in execution.
5. **Stay disciplined.** The system uses few colors, few typefaces, restrained imagery. Consistency is what creates recognition.
6. **Work on a phone.** All visual choices must hold up on mobile. The customer reads this on a phone between jobs, often with one bar of signal.

## Site structure

The homepage sells the brand. Segment-specific pages sell the segment-specific use case. The top nav includes a "Who is this for" dropdown linking to:

- `/for/contractors`
- `/for/property-managers`
- `/for/warehouses`
- `/for/manufacturers`

Same brand, same offering, same palette and type. Different surface examples, different vocabulary at the margin.

## Homepage structure

Eight sections, scroll-based, no slide breaks. Full copy is in `homepage-copy.md`. Brief overview for design context:

1. **Hero** — *Custom training, made for how the work actually happens. Built from your team's existing documentation.* Image: single conceptual illustration establishing tone.
2. **The materials exist. They go unused.** — the binder problem named. Image: conceptual illustration of transmission attempted but not received.
3. **The real question is whether the crew actually knows.** — comprehension as the brand's core question. Image: conceptual illustration about interior structure made visible.
4. **What the work is.** — introduction of the practice and its principle. Image: conceptual illustration about transformation between two states.
5. **The process.** — three-beat mechanical description. No image.
6. **What it costs.** — three pricing tiers stated plainly. No image.
7. **A demo.** — link to the ten-minute LOTO module. Optional thumbnail.
8. **A short call.** — link to book the discovery call. No image.

The page should flow as continuous text-with-image rhythm. Sections 5-8 are deliberately lean on imagery to give the upper sections space to land.

## Mobile-first considerations

The primary device is a customer's phone, often used in a vehicle, on a job site, or in an operational setting. Design implications:

- Type must hold up at mobile sizes without straining
- Imagery must be legible at narrow widths
- The hero should establish the brand within the first phone-screen of scroll
- CTAs (Open the demo, Book the call) must be clearly tappable
- The whole page should load fast — minimal external dependencies, optimized images, no heavy frameworks

## What's still open

Decisions deliberately left to production:

- Exact font weights for headlines
- Letter-spacing tuning
- Mobile typography sizing
- Whether utility sans stays IBM Plex or swaps to Inter
- Imagery — to be developed iteratively, starting with the four primary homepage images (hero, section 2, section 3, section 4)
- Logo / wordmark — likely just "SOPs Nobody Reads" set in Lora with deliberate proportions. No separate mark needed. The system itself is the recognition.
- Application beyond the homepage — module player UI, email signature, invoice template, proposal template, segment-page layouts

## What success looks like

A visitor to the site should:

- Recognize within five seconds that this is a serious practice, not a marketing site
- Understand within fifteen seconds what the offering is
- Feel the brand has weight without performing weight
- Encounter no element that triggers the *"another vendor"* shutdown
- Want to see the demo or book the call

A designer reviewing the brand should:

- See immediately that every choice is in service to a coherent worldview
- Recognize the discipline (few colors, one typeface family, restrained imagery) as deliberate rather than budget-driven
- Be able to extend the system to new surfaces (modules, invoices, proposals, segment pages) without ambiguity about how
- Have no questions about what the brand *isn't* — the disqualifications are as clear as the qualifications

## Contact

Sean Roth
sean@seanroth.ai

Working repository: github.com/sean-roth/phonebooth (docs/branding folder)
