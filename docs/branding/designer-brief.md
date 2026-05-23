# Designer Brief — SOPs Nobody Reads

A single document for the designer working on the SOPs Nobody Reads visual identity. Synthesizes the brand foundations, palette, typography, and homepage into a working brief. The other files in this folder (brand-foundations.md, palette.md, typography.md, homepage-copy.md, cold-call-pitch.md, discovery-questions.md) provide deeper rationale where needed.

---

## What the brand is

SOPs Nobody Reads is a small instructional design practice run by Sean Roth, working with Chicago-area trade contractors (electrical, mechanical, fireproofing, sheet metal, glazing, similar). The practice takes a contractor's own written procedures — SOPs, safety manuals, equipment documentation — and converts them into interactive training modules that crews actually finish.

The brand essence: **tribal knowledge deserves to be transmitted.** Craft has lineage. The trades are older than digital technology and will outlive it. Domain knowledge cannot be generated; it can only be transmitted. The practice exists to make that transmission work.

The closest professional analog for the brand's character: **a luthier.** Builds the instrument that lets the musician's craft be heard. Doesn't write the music. Doesn't play the music. Is a master of his own craft precisely because he knows he is not the musician. The luthier has no cosplay risk because his identity is built on the clear distinction between his work and the musician's.

The brand's working phrase for its own posture: **aiding in craftsmanship.**

## What the brand is not

The brand explicitly rejects:

- **The safety/compliance category aesthetic.** No hi-vis yellow or orange. No hardhat imagery. No jobsite stock photography. No construction-site visual cues of any kind. The brand is in service to the trades, not from them.
- **Tech-vendor aesthetics.** No gradients, no abstract isometric illustrations, no friendly mascots, no startup minimalism. The brand is not a SaaS product.
- **Performance of authenticity.** No rustic costume aesthetics. No vintage typography as cosplay. No Field Notes-style craft heritage performance.
- **Self-decoration.** Design that draws attention to itself is design that has failed. The visual identity supports the message and the customer journey, playing second to both.

## The cosplay test

The single most important test the visual identity must pass: **does this visual / word / image suggest the brand is trying to be the customer?**

If yes — kill it. The trades respect *other craft*. They don't respect imitation of their craft. The brand's dignity comes from being clearly itself — editorial, transmission-oriented, considered — in service to the customer's craft. Like a luthier. Like a scribe. Like a cartographer.

## Reference territory

The visual identity should draw from:

- **Editorial design** — serious nonfiction publishing, Phaidon, NYRB Classics, longform editorial layouts
- **Reductive conceptual illustration** — Christoph Niemann is the closest single reference (his New Yorker covers and Sunday Sketches work). Single ideas made concrete through minimum elements.
- **Sequential art logic** — panel pairs, before/after compositions, visual transitions that show change between two states
- **Reference and archival aesthetics** — well-made technical references, museum design, vintage scientific illustration

The visual identity should avoid:

- Anything from the safety/compliance category (ClickSafety, Vector, Avetta visual language)
- Construction-site visual cues
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
2. **Flat, graphic shapes.** No photorealistic rendering. No detailed textures. Reduced forms — a bird as silhouette, a building as rectangle, a tool as outline.
3. **Restricted internal palette.** Each image uses no more than two or three colors, drawn from or harmonizing with the brand palette where possible.
4. **Conceptual punch.** Each image carries a single idea that "clicks" when the viewer understands it. The image isn't decoration — it's another channel for the message.
5. **Editorial restraint.** The image should never compete with the text it accompanies. It exists to support and reinforce, not to be admired.

All imagery is produced through AI image generation (Replicate, current best model), then curated against these criteria. Most generated images will be rejected. The discipline of rejection is what creates a consistent visual system rather than a stream of AI outputs.

No literal trade imagery. No hardhats, no construction workers, no jobsite scenes. The imagery transmits abstract ideas — transmission, comprehension, structure, translation — not depictions of the customer's world.

## What the visual identity has to do

Six things, in priority order:

1. **Make the message land.** The brand voice is direct, confessional, specific. Visual choices must support that voice, not soften or decorate it.
2. **Establish dignity.** The contractor must feel he is encountering a serious practice, not a marketing site.
3. **Pass the cosplay test.** Nothing in the visual identity should suggest the brand is from the trades.
4. **Read as old work in modern form.** The aesthetic should feel rooted — editorial, archival, considered — while being clearly contemporary in execution.
5. **Stay disciplined.** The system uses few colors, few typefaces, restrained imagery. Consistency is what creates recognition.
6. **Work on a contractor's phone.** All visual choices must hold up on mobile. The customer reads this on a phone between jobs, often with one bar of signal.

## Homepage structure

Eight sections, scroll-based, no slide breaks. Full copy is in `homepage-copy.md`. Brief overview for design context:

1. **Hero** — two-line statement of the offering. Image: single conceptual illustration establishing tone.
2. **The materials exist. They go unused.** — the binder problem named. Image: panel pair showing transmission attempted vs received.
3. **The real question is whether the crew actually knows.** — comprehension as the brand's core question. Image: cross-section or structural diagram.
4. **What the work is.** — introduction of the practice and its principle. Image: panel pair showing dense text becoming organized constellation.
5. **The process.** — three-beat mechanical description. No image.
6. **What it costs.** — three pricing tiers stated plainly. No image.
7. **A demo.** — link to the ten-minute LOTO module. Optional thumbnail.
8. **A short call.** — link to book the discovery call. No image.

The page should flow as continuous text-with-image rhythm. Sections 5-8 are deliberately lean on imagery to give the upper sections space to land.

## Mobile-first considerations

The primary device is a contractor's phone, often used between jobs in a truck cab. Design implications:

- Type must hold up at mobile sizes without straining
- Imagery must be legible at narrow widths (sequential-art panels may need to stack vertically on mobile)
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
- Application beyond the homepage — module player UI, email signature, invoice template, proposal template

## What success looks like

A contractor visiting the site should:

- Recognize within five seconds that this is a serious practice, not a marketing site
- Understand within fifteen seconds what the offering is
- Feel the brand has weight without performing weight
- Encounter no element that triggers the *"another vendor"* shutdown
- Want to see the demo or book the call

A designer reviewing the brand should:

- See immediately that every choice is in service to a coherent worldview
- Recognize the discipline (few colors, one typeface family, restrained imagery) as deliberate rather than budget-driven
- Be able to extend the system to new surfaces (modules, invoices, proposals) without ambiguity about how
- Have no questions about what the brand *isn't* — the disqualifications are as clear as the qualifications

## Contact

Sean Roth
sean@seanroth.ai

Working repository: github.com/sean-roth/phonebooth (docs/branding folder)
