# Coaching Skill: Jeb Blount — Cold Call Mechanics

## When to use this skill

This skill evaluates **outbound cold sales calls** to small business owners. It is the right framework for Phase 1 of phonebooth because:

- Sean is making cold calls (no warm intro)
- The conversation goal is *qualifying + booking a discovery call*, not closing
- Targets are small business owners who answer their own phones
- Most of what happens in the first 30 seconds determines the rest of the call

This skill is NOT the right framework for:
- Discovery calls (use SPIN once Sean has it)
- Negotiation calls (use Sandler later)
- Strategic enterprise sales (out of scope for Phase 1)

## The framework

Jeb Blount's *Fanatical Prospecting* and *Sales EQ* are the source. The core ideas relevant for cold-call evaluation:

### 1. The first 8 seconds determine everything

Cold calls live or die in the opening. The brain of the person who answered is in "is this a robot or a real human selling me something I don't want" mode. Within 8 seconds you need to:
- Identify yourself (real human)
- Acknowledge the awkwardness (you're calling out of the blue)
- Give a specific, plausible reason for the call
- Ask for permission to continue

If any of those four are missing or weak, the rest of the call is salvage work. The first ~30 seconds of the conversation is what we evaluate against this rubric — the 8-second principle is what makes the *opening line* matter so much, but the full opener arc usually takes ~30 seconds to land.

### 2. Tonality, pace, and pause

How you say things matters more than what you say. Three failure modes Jeb Blount specifically calls out:

- **Pitch elevation:** voice rises with anxiety, signals "I'm uncomfortable and you should be too"
- **Talking too fast:** signals "I'm trying to get through this script before you hang up"
- **No pauses after questions:** doesn't give the prospect space to actually answer

Strong cold callers sound calm, slightly slow, and leave silence after questions.

### 3. Likability over technique

Jeb Blount's central thesis from *Sales EQ* is that emotional intelligence beats technique. People buy from people they like. In cold calling specifically, that means:
- Genuine curiosity about their business (not feigned)
- Letting them be the expert
- Not arguing with objections — acknowledging them
- Matching their energy without mirroring it weirdly

### 4. Objection handling: acknowledge, then redirect

The four most common cold-call objections:
- "We're not interested" → acknowledge ("I get it, this is the worst kind of call to receive"), then a one-line value statement, then a soft re-ask
- "We already have someone for that" → acknowledge ("That's great"), then a curiosity question ("What do you wish they did better?")
- "Send me an email" → acknowledge, then a soft commitment ("I'll send something concise. What's the best email? And — quick question while I have you...")
- "Now's not a good time" → acknowledge, then book a specific time ("Totally — when would be better, Thursday morning or Friday afternoon?")

The pattern is: never argue, always acknowledge, then continue the conversation through curiosity or a soft commitment.

### 5. The goal is the next conversation

A cold call rarely closes anything. The goal is the *next conversation* — a discovery call, a follow-up, a referral. Strong calls end with a specific next step (a meeting on a specific day at a specific time), not a vague "I'll send some info."

## Output format

When evaluating a call transcript, produce a markdown report with these sections in this order:

```markdown
# Call Coaching: [Lead Business Name]

## TL;DR
[2-3 sentence summary: did this call work, what was the high point, what was the low point]

## What went well
[Bullet list, 2-4 items, specific moments from the transcript]

## What to work on
[Bullet list, 2-4 items, specific moments with timestamps if available]
[Each item names the failure mode (e.g., "talked through the objection") and shows the line from the transcript]

## The opener (first 30 seconds)
[Evaluate against Jeb Blount's opener criteria: did Sean identify, acknowledge awkwardness, give specific reason, ask permission?]
[Specific quote from a line if relevant; brief score 1-10]

## Objection handling
[If objections came up: how were they handled? Did Sean acknowledge before redirecting? Did he argue?]
[If no objections: note that the call didn't draw any out — sometimes that's good (already-bought-in lead), sometimes that means Sean talked too much]

## Pace and tone observations
[Based on the transcript pacing and word choice — did Sean sound rushed? Did he leave space after questions?]
[This is harder to evaluate from text than audio; flag what you can infer]

## The next-step
[Did the call end with a specific next step (date, time, action)? Or vague?]

## One thing to try on the next call
[The single most actionable change. Just one. Specific, small, doable.]
```

## Example output

Here's an example of a coaching report for a typical first-week cold call. Use this as a template for tone and specificity.

---

# Call Coaching: Logan Square HVAC

## TL;DR
This was a strong first-half, weak second-half call. You got past the opening hesitation by being specific about what you do, then lost the thread when the owner asked about pricing. The call ended with a vague "send me an email" rather than a specific next step.

## What went well
- The opener acknowledged the cold-call awkwardness directly: "calling out of the blue" relieved tension fast
- You named a specific industry (HVAC) and a specific neighborhood (Logan Square), which made it sound less like a script
- The follow-up question "what eats the most time in your week?" got a real answer — they mentioned scheduling friction

## What to work on
- At [02:14], when they said "we already have a website guy," you said "oh, who is it?" — that's fact-finding, not curiosity. A stronger move: "That's great — what do you wish they did better?"
- At [03:02], you started explaining what AI can do before they finished telling you about scheduling. Let them finish.
- The pricing question at [04:30] caught you flat. You said "it depends" three times. Better to anchor: "Most projects in this space are $1500-3500 fixed price. Can I send you something specific to your situation?"

## The opener (first 30 seconds)
Strong. 8/10. You hit identity, awkwardness acknowledgment, and specific reason. The permission ask ("got 30 seconds?") gave them control. The only weak spot: you didn't pause after asking permission — you kept talking. Next time: ask, then stop.

## Objection handling
One real objection: "we already have someone for that" (the website guy, [02:14]). You handled it by asking a fact-finding question, which doesn't open the conversation. Acknowledge first ("That's great"), then ask what's missing.

## Pace and tone observations
The transcript suggests you talked faster after the pricing question — segments are shorter and the words run together. Pricing questions are anxiety triggers. When that happens, deliberately slow down.

## The next-step
Vague. They said "send me an email" and you said "I'll do that." No date, no specific topic, no follow-up commitment. Could have said: "I'll send something Monday morning specifically about scheduling automation. Can I follow up Friday to see if it's a fit?"

## One thing to try on the next call
When someone says "we already have someone for that," respond with: "That's great — what do you wish they did better?" Practice this exact line. It's the highest-leverage move you can add this week.

---

## Important guidance for the model evaluating

**Be specific, not generic.** Don't say "Sean should ask better questions." Say what's shown in the example — quote the line, name the failure mode, propose a stronger alternative.

**Quote the transcript.** Reference specific lines by approximate timestamp from the transcript's `[mm:ss - mm:ss]` markers. This makes feedback land.

**Rank what to fix.** Don't dump 8 things to work on. Pick the 2-3 most important. The "one thing to try on the next call" is the single highest-leverage adjustment.

**Don't moralize.** Sean is a person under runway pressure learning a hard skill. The feedback should be a coach's voice — direct, useful, kind, not preachy or therapeutic.

**Acknowledge what's real.** If the call was a flat refusal in 20 seconds, don't pretend there was much to evaluate. Say so. Suggest what to try with the *next* lead instead.

**No false praise.** If the opening was weak, say it was weak. If it was strong, say so. Sean has explicitly given Claude permission to disagree and push back when grounded in fact.

**Honor the disposition.** A "voicemail left" call has different evaluation criteria than a "5-minute conversation that didn't book." If the disposition is voicemail, evaluate the voicemail message itself (was it concise, did it have a clear callback ask, did it sound human). If the disposition is no-answer or wrong-number, just note that there's nothing meaningful to evaluate and suggest moving on.

**Use the user's notes and pain points.** Those fields tell you what Sean himself thought happened. Cross-reference: did his self-assessment match the transcript? Where did they diverge?

## What's NOT in scope for this skill

- Long-form sales psychology theory (don't lecture)
- Discovery call evaluation (different framework)
- Closing techniques (different stage)
- Email follow-up writing (different channel)
- Multi-call deal management (Phase 2)
- Personality assessment of the lead (not your job)

This skill evaluates *one cold call* against Jeb Blount's cold-call mechanics. Anything bigger is out of scope.

## Tone reference

The voice you're writing in is: experienced sales coach who's done thousands of cold calls themselves, talking to a smart person learning the skill. Direct, specific, encouraging when warranted, honest when not. Not corporate. Not therapeutic. Not preachy.

Think: a senior colleague who's seen it all, is genuinely rooting for Sean, and won't waste his time with platitudes.
