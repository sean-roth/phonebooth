# Manual Before Automation

A principle for deciding when and how to build automation, AI features, or agentic systems.

## The principle

**Use as little intelligence and compute as the task allows. And the human has to walk the path first.**

Two halves, both load-bearing.

The first half is about resource discipline. Frontier models are powerful enough to brute-force most problems, which makes them tempting to reach for by default. They also cost more, fail in more interesting ways, and are harder to debug than deterministic code. Most tasks want less intelligence than feels natural to assign them. The right question is not *"how do I use AI for this?"* but *"how little AI does this actually need?"* Cut where you can. Invest where it's needed.

The second half is about scoping discipline. You cannot write a useful spec for a system you haven't lived inside. Every assumption made in advance is wrong in a way you won't detect until the system is built and producing wrong outputs. Manual work is not what you do until automation is ready — manual work is how you figure out what the automation should be.

## Why it works

When you do the task manually:

- You see what data is actually available, not what you imagined would be available
- You notice which decisions are genuinely hard versus which are deterministic in disguise
- You discover failure modes that wouldn't surface in a spec written from imagination
- You learn which signals predict the outcome you care about and which are noise
- You feel where the friction is — which often turns out to be different from where you guessed

This understanding cannot be transferred via prompt. It has to be earned by exposure.

## Receipts

### LinkedIn outreach

Ran a 400–500 message campaign to small-contractor LinkedIn profiles with a Claude agent. Zero responses. The agent dutifully sent the messages; nothing came back.

The problem was not the agent. The problem was that LinkedIn DMs as a channel had collapsed for this audience — saturated by AI-generated outreach, ignored by trade owners who don't check the platform. Manual outreach to even 20 profiles would have surfaced the same null result in two hours instead of two weeks. The build replaced the manual validation that would have killed the project earlier.

### Lead generation feature

Initial plan: build a "super lead gen agent" with Claude Code, deep enrichment pipeline across multiple data sources (Google Maps + LinkedIn + Firecrawl + Twilio), frontier model driving decisions about which leads to surface.

Hand-prepped 27 leads from Google Maps in roughly an hour. Discovered:

- There is very little data on owner-operator trade contractors. Name, phone, address, sometimes a website link, star rating, a handful of reviews. That is the whole dataset.
- There is no enrichment to do. The polished contractors might have a LinkedIn, but the targets do not. The "deep enrichment pipeline" was solving a problem that did not exist.
- The intelligence required is minimal. Trajectory analysis is pure stats. Signal extraction is keyword matching. The only place a model earns its keep is a single one-sentence hook synthesis at the end.

Result: the feature collapsed from "Claude Code agent with frontier model orchestration" to "scraper, sorter, and a 4B local model for the final synthesis step." Cost dropped from ongoing API spend to near-zero. Build time dropped from weeks to one focused day. Failure modes dropped from agentic chaos to deterministic bugs.

The hour of manual prep was worth a week of building the wrong thing.

### Cold call script

Initial script was written from imagination — what a sales script "should" look like. After one real call attempt that produced anxiety and avoidance, the script needed two revisions before it sounded like something a person would actually say. The revisions came from hearing the script in the mouth and noticing which phrases triggered cringe.

A script written without trying to say it out loud is a guess. The mouth knows things the page doesn't.

## How to apply the principle

Before building any system that uses AI or automation, ask:

1. **Have I done this manually enough to know what the system should do?** If no, do it manually first. Even badly. Even for an hour.

2. **What is the smallest amount of intelligence this task needs?** Deterministic rules where possible. Embeddings before generation. Small models before large. Frontier models only when the task genuinely requires reasoning under ambiguity.

3. **What data is actually available?** Not what would be nice to have. Not what a polished version of the data source would expose. What is *literally there* when you look at it.

4. **Where will I find out I'm wrong?** Manual work surfaces wrongness fast. Building surfaces wrongness slowly. Bias toward the faster feedback loop.

5. **What is the human doing that the system isn't?** The system exists to remove friction from the human doing skilled work. Anything the system does that doesn't serve that goal is overhead.

## When to override the principle

There are cases where building first is right:

- **The manual task is genuinely impossible at human scale** (translating 50,000 documents, processing real-time video). Then build, but build the smallest possible system that handles it.
- **The manual task has been done by others and the patterns are well-documented** (standard CRUD app, standard form processing). You don't need to live it; you can read it.
- **The cost of building is trivial and the cost of manual work is large** (one-off script to dedupe a list). Just build the script.

Most product-building decisions don't fit these exceptions. When in doubt, do it manually first.

## What this principle prevents

- Building systems that solve imagined problems instead of real ones
- Using more compute, model size, or complexity than the task needs
- Skipping the learning step that turns a vague intuition into a specific spec
- Treating "use AI" as a goal rather than a tool

## What this principle enables

- Tighter, cheaper, more reliable systems
- Specs that match reality
- Faster recovery when an approach is wrong (you find out in an hour, not a week)
- Natural project scoping — the system reveals its own shape through manual exposure
- The ability to recognize when "no AI" is the right answer

## On the relationship between this principle and the work

The cold call cockpit Sean is eventually building — phonebooth grown into a lead gen feature, a CRM, a parallel dialer, a recording reviewer — is the same pattern at a larger scale. The cockpit's job is to remove everything between Sean and the prospect except the conversation itself. Lead pre-loaded. Script in peripheral vision. Recording automatic. Notes captured in the moment. Follow-up email one click away.

The cockpit can only be built well after the calls have been made manually enough times to know which frictions matter and which don't. Building the cockpit before the calls would produce a cockpit optimized for imagined frictions, not real ones.

The training modules Sean sells follow the same principle at the customer level. Trade owners want training that lets their crews complete the learning without managing a binder of paperwork. The product removes friction from the human doing skilled work, exactly as the cockpit removes friction from the salesperson doing skilled work. The principle is consistent through the whole business.

Strip the system down so the human can be present.

## Status

Principle adopted Sunday, May 10, 2026, after the lead gen feature scoping conversation. Add new receipts as they accumulate.
