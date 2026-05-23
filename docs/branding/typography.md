# Typography — SOPs Nobody Reads

## The choice

| Role | Typeface | Source |
|------|----------|--------|
| Display (headlines) | Lora | Google Fonts (free) |
| Body (reading text) | Lora | Google Fonts (free) |
| Utility (captions, footers, fine print) | Neutral sans-serif — see below | Multiple options, see below |

## Why Lora

Lora is a free, open-source serif designed for sustained reading on screens. It sits in the workhorse-editorial register — close in feel to Tiempos (a respected commercial typeface used by major publications) but with slightly warmer, more humanist letterforms.

The reasons it fits this brand specifically:

1. **It doesn't perform.** Lora's letterforms are calm and direct. The typeface gets out of the way and lets the words be the personality. This matches the brand principle that *design should support the message and the customer journey, playing second to both.*

2. **It carries weight.** The letterforms have substance — slightly chunky, with robust serifs that hold up at small sizes. The typeface feels like it has presence without performing literary seriousness.

3. **It reads well in long passages.** Designed specifically for body text on screens, with moderate contrast and proportions that don't fatigue the eye. This matters because the brand's voice is text-forward.

4. **It works against the palette.** Lora's letterforms have enough weight to hold up in forest green against cream without losing definition. The slight warmth of the humanist forms complements the cream background.

5. **The name carries a private reference.** Lora echoes LoRA (Low-Rank Adaptation, a fine-tuning technique in AI work). Not a public-facing detail, but a small inside recognition that sustains the work over time.

## Why one family for everything

Using Lora for both display and body keeps the typographic system tight. The brand has a unified voice — same letterforms at every scale, with hierarchy created through size and weight rather than typeface change. This is the more disciplined choice than pairing a display serif with a different body serif, and it reduces the visual complexity the page has to manage.

The exception is utility text (captions, footers, fine print), where a neutral sans-serif is used for clarity at small sizes.

## Utility sans-serif — working options

The utility sans-serif handles small functional text only. Its job is to recede — readable at 11-13px without competing for attention.

Three options, in order of recommendation:

**IBM Plex Sans** (Google Fonts, free)
Continuity with seanroth.ai, which already uses Plex. Slightly distinctive without being loud. Works well at small sizes. The default if you want quiet harmony with the existing portfolio.

**Inter** (Google Fonts, free)
Designed specifically for digital interfaces. Maximally neutral — the typeface most likely to disappear into the work it supports. Slightly more contemporary than Plex.

**GT America** (commercial, not free)
A higher-quality neutral sans, used widely in editorial design. Worth mentioning for completeness but not necessary for the MVP brand.

**Recommendation:** Start with IBM Plex Sans. Reasonable continuity with the existing personal brand, no licensing cost, easy to deploy. If during production it feels too distinctive or doesn't harmonize well with Lora, swap to Inter.

## Weights — to be decided in production

The full Lora family has weights from 400 (Regular) through 700 (Bold) plus italics. The brand probably needs three weights total:

- **Regular (400)** for body text
- **Medium (500) or SemiBold (600)** for headlines and emphasis
- **Italic (400)** for subheads, quotes, and rhetorical emphasis

The exact weight for headlines (500 vs 600) should be decided when type is rendered in actual production — sometimes the right weight depends on the screen, the rendering engine, and how the type sits against imagery. Bold (700) is probably too heavy for the brand's restrained register; SemiBold is the more likely choice.

For the utility sans-serif: probably just Regular (400) at small sizes.

## Type sizes — starting recommendations

These are working values to start from, not final. Adjust during production based on real screens.

**Desktop:**
- H1 (page hero): 38-42px, Lora Medium or SemiBold
- H2 (section headers): 26-32px, Lora Medium
- H3 (subsections): 20-22px, Lora Medium or Italic
- Body: 16-17px, Lora Regular, line-height 1.6-1.7
- Utility (captions, footers): 12-13px, IBM Plex Sans Regular

**Mobile:**
- H1: 30-34px
- H2: 22-26px
- H3: 18-20px
- Body: 16px (don't go smaller — readability matters more than scale)
- Utility: 12px

## Mobile note

Worth checking during build: Lora's letterforms hold up well at small sizes because the serifs are robust rather than ornamental, but mobile screens vary in pixel density and the body text size may need slight adjustment. The test is whether body text at 16px on a phone screen reads comfortably without straining. If it does, the typography is working. If it doesn't, try 17px or adjust line-height.

## What this typography system is not

- **Not high-contrast or elegant.** Lora is humanist and warm rather than refined. A more elegant serif (Domaine, Cormorant, Bodoni) would betray the brand's working-practice register.
- **Not modern or tech-adjacent.** No geometric sans (Avenir, Futura, Circular). The brand reads as editorial, not as tech.
- **Not retro or nostalgic.** No vintage display faces, no woodtype, no overtly historical typefaces. The brand is contemporary in its restraint.
- **Not custom.** No commissioned typefaces, no logo-as-wordmark with custom letterforms. The brand uses well-made existing tools rather than performing uniqueness through type.

## Implementation notes for the designer

When loading Lora from Google Fonts, include only the weights actually used to keep the page load light. The minimum useful subset:

```
Lora: 400, 500 or 600, 400-italic
IBM Plex Sans: 400
```

The font-display strategy should be `font-display: swap` so text renders immediately in fallback fonts while Lora loads. Fallback stack:

```css
font-family: 'Lora', Georgia, 'Times New Roman', serif;
font-family: 'IBM Plex Sans', system-ui, sans-serif;
```

## Open questions to resolve in production

1. **Exact weight for headlines** — Medium (500) or SemiBold (600). Decide when rendering against the palette in real layouts.

2. **Letter-spacing for headlines** — Lora at large sizes may benefit from slight negative tracking (around -0.3px to -0.5px) to tighten the headline rhythm. Test in production.

3. **Mobile body text size** — 16px or 17px depending on screen density and line-length.

4. **Whether the utility sans-serif stays IBM Plex Sans or swaps to Inter** — depends on how the two typefaces feel together in real layouts.

These are tuning decisions, not structural ones. The typeface choice (Lora) and the role definitions (display + body in serif, utility in sans) are committed.
