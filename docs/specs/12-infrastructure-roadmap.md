# 12 — Infrastructure Roadmap: From Learning System to Revenue System

## Purpose of this document

Phase 1 phonebooth runs on Sean's OptiPlex 9020 in Conifer. That's correct for a learning system being built under runway pressure — the hardware is already there, the cost is zero, and the design assumes throwaway-and-rebuild after field testing.

If phonebooth becomes Sean's revenue system, the OptiPlex is no longer the right place for it. This spec captures the infrastructure progression from "good enough to learn" to "good enough to depend on for income."

This is not a Phase 2 build plan. It's a decision-staging document so the migration question has a frame when it comes up.

## When this matters

Don't migrate prematurely. The OptiPlex setup is fine until any of these are true:

- **Revenue is happening regularly.** A booked discovery call per week with paying conversions monthly. At that point, downtime costs real money.
- **Reliability becomes load-bearing.** A client expects you to be reachable; missing a callback because ngrok rotated its URL is a real problem.
- **You're traveling.** OptiPlex going offline because you're not home to power-cycle it after a power blip is a real problem.
- **Wildfire evacuation forces an OptiPlex shutdown.** Conifer wildfire risk is documented. A revenue system that goes down during evacuation is a problem when income depends on it.
- **The Chicago move happens.** OptiPlex moves with you, but transit downtime + new ISP setup means days offline.

If none of these are true, stay on the OptiPlex. The migration is overhead you don't need yet.

## The progression

Three stages, each appropriate to a different level of dependence on the system.

### Stage 1: OptiPlex + ngrok free tier (where you are now)

- **Compute:** OptiPlex 9020 at home
- **Public access:** ngrok free tier, URL rotates on restart
- **Database:** SQLite local file
- **Backups:** none (or manual `cp database/database.sqlite somewhere`)
- **Monitoring:** none
- **Cost:** $1.15/mo (Twilio number) + variable Twilio minutes

**Good for:** learning, Phase 1, the first month of calling. Throwaway shape. Friction is fine; it's not revenue-bearing.

**Not good for:** anything you depend on.

### Stage 2: OptiPlex + Cloudflare Tunnel (a small upgrade, free)

- **Compute:** OptiPlex 9020 at home
- **Public access:** Cloudflare Tunnel (cloudflared) with a real domain
- **Database:** SQLite local file
- **Backups:** add a daily cron that copies SQLite somewhere safe (Backblaze B2, S3, even Google Drive via rclone)
- **Monitoring:** UptimeRobot free tier pinging your phonebooth.yourname.com
- **Cost:** $1.15/mo Twilio + ~$12/year domain + variable Twilio minutes

**What changes:** stable public URL, runs as a daemon (survives reboots), Cloudflare's network is far more reliable than ngrok free tier. You still depend on the OptiPlex being on and your home internet being up. But the tunnel itself is no longer the weak link.

**Good for:** the transition period when you're starting to depend on the system but don't yet want to deal with VPS management. Probably 1-3 months.

**Not good for:** anything where being unreachable for hours is a real problem.

### Stage 3: VPS deployment (when revenue makes it worth $5-12/mo)

- **Compute:** small VPS (Hetzner, DigitalOcean, Linode — $5-12/mo for what phonebooth needs)
- **Public access:** real public IP with a real domain
- **Database:** still SQLite (it's fine for one user) or Postgres if you want to integrate Twenty CRM
- **Backups:** automated daily backups to object storage (B2, S3) — most VPS providers have built-in snapshot tooling too
- **Monitoring:** UptimeRobot or BetterUptime, plus error tracking via Sentry free tier
- **Cost:** $1.15/mo Twilio + $5-12/mo VPS + ~$12/year domain + maybe $1-3/mo for backup storage + variable Twilio minutes

**What changes:** your laptop being closed, OptiPlex being off, home internet being out — none of these affect the system anymore. The VPS sits in a datacenter with redundant power and network. Uptime measured in 99.9%+ rather than "whatever your house is doing."

**Good for:** revenue-bearing operation, the long-term home of the system.

**Cost reality:** ~$10-20/month for the whole hosting stack. At one client paying $1k/month, that's 1-2% overhead. Trivially worth it.

## Why this isn't a "do it now" recommendation

Three reasons.

**One: you don't know if the system is worth migrating yet.** Field testing this week tells you whether phonebooth as designed is the right tool. If after a week you decide to rebuild from scratch (which Sean has explicitly anticipated), you'd have migrated infrastructure for the wrong system. Wait until the architecture stabilizes.

**Two: VPS setup is real work.** Probably 4-8 hours done well — provisioning, deploying Laravel, getting the domain DNS right, setting up Twilio webhooks against the new URL, getting backups working, getting monitoring in place. That's a Phase 2 sprint, not a "before Monday" task.

**Three: Stage 2 (Cloudflare Tunnel) is genuinely good enough for the first month.** It's a 30-minute upgrade that solves the URL rotation problem without any of the VPS complexity. You can sit at Stage 2 until revenue is real.

## Migration triggers (concrete)

Move from Stage 1 to Stage 2 when:

- You restart ngrok more than twice in a week to update Twilio config
- You leave town and worry about whether the OptiPlex is still serving Twilio webhooks
- You have a domain you control that you'd want phonebooth on

Move from Stage 2 to Stage 3 when:

- Any of the "when this matters" conditions above become true
- A client asks for your phone system to be reliable as a contractual matter
- You have $1,000+/month in recurring revenue from work phonebooth helped book
- You're seriously planning the Chicago move

Don't move on aesthetics. Move on triggers.

## What VPS (Stage 3) actually looks like

For when you're ready, here's the rough shape. This is not a build spec — it's enough for you to evaluate the lift.

**VPS provider:** Hetzner ($4-5/mo for CX22 with 2 vCPU, 4GB RAM, 40GB SSD, in Ashburn or Hillsboro for low Twilio latency). DigitalOcean and Linode are similarly priced. All fine.

**OS:** Ubuntu 24 LTS (matches the OptiPlex setup, minimal surprises).

**Web stack:**
- nginx as the reverse proxy (handles HTTPS via Let's Encrypt / Certbot)
- PHP-FPM for Laravel
- SQLite stays as the database (one user; no need for Postgres)
- supervisord or systemd for any background processes

**Domain + DNS:**
- A domain you control (phonebooth.yourname.com is fine)
- DNS A record pointing at the VPS IP
- Let's Encrypt cert auto-renewing

**Deployment:**
- Git push to a branch that auto-deploys (could use a service like Forge, or just a `git pull && composer install --no-dev && php artisan migrate` cron)
- For Phase 2, manual SSH-and-deploy is fine

**Backups:**
- Daily SQLite snapshot uploaded to Backblaze B2 (~$0.005/GB/month — phonebooth's database will be tiny, so basically free)
- Keep 30 days of snapshots, prune older

**Monitoring:**
- UptimeRobot free tier pinging the dashboard every 5 minutes
- Sentry free tier for error tracking (5K errors/month free)

**Twilio webhook update:**
- Point Twilio TwiML App webhooks at the new public URL
- Same code; just different URL in `.env`

**Phase 2 additions worth considering at this stage:**
- Twenty CRM (self-hosted on the same VPS, or connect to a managed Twenty if available)
- Object storage for any growing file storage (discovery transcripts could move from local FS to B2 if volume grows)
- Email sending for follow-ups (Resend, Postmark — both have free tiers for low volume)

## What stays the same in any stage

The Laravel application code. The database schema. The Twilio integration. The Claude Desktop coaching workflow. Sean's relationship with the work.

The progression is purely about *where the system runs*, not *what the system is*. This makes migration genuinely incremental — you're not rebuilding the system, just relocating it.

## What this means for the OptiPlex's future

The OptiPlex stays valuable even after phonebooth migrates:

- Clara development continues there (multi-agent system needs the local compute)
- SOPs Nobody Reads stays there
- Compel English R&D stays there
- Any local-only AI work (Whisper experiments, local model evaluations) stays there
- The OptiPlex becomes a development machine instead of a production server, which is what it should have been all along

Phonebooth migrating off the OptiPlex doesn't reduce the OptiPlex's value. It clarifies what each machine is for.

## A note on the Chicago move

When the move happens, Stage 3 (VPS) means phonebooth doesn't care. The system is in a datacenter; you change physical locations and your network and your morning routine, but phonebooth is just a domain name that resolves to the same IP it always did.

Stages 1 and 2 require shuttling the OptiPlex through a transit period and reestablishing home network. That's days of downtime if you're not careful, and it's exactly the kind of thing that would happen at the worst possible moment for a revenue-bearing system.

This is one of the strongest arguments for migrating *before* the move, not after. If the timeline is "Chicago move in 3-6 months and revenue is happening by then," Stage 3 should happen ahead of the move, not during.

## Decision log for future Sean

When the migration question comes up, this is the order to think about it in:

1. Is any "when this matters" condition true?
   - No → stay where you are, don't migrate on aesthetics
   - Yes → continue
2. Is it a tunnel reliability problem (ngrok rotating URLs, etc.) that Stage 2 would solve?
   - Yes → Cloudflare Tunnel + domain, 30 minutes of work, done
   - No → continue
3. Is it a "I depend on this and the OptiPlex isn't enough anymore" problem?
   - Yes → Stage 3 (VPS), 4-8 hours of work, plan a Phase 2 sprint for it
   - No → reassess; you might be solving the wrong problem

Don't conflate "this would be cooler" with "this would be necessary." Migration before need is wasted work.

## Summary

Three stages, three decision points:

| Stage | Where | Cost | Good for |
|---|---|---|---|
| 1 | OptiPlex + ngrok free | $1.15/mo + Twilio variable | Phase 1 learning |
| 2 | OptiPlex + Cloudflare Tunnel | $1.15/mo + $1/mo domain + Twilio variable | Transition period (1-3 months) |
| 3 | VPS + real domain | ~$10-20/mo total | Revenue-bearing operation |

You're at Stage 1. Stay there until calling tomorrow tells you what you're actually building. Move to Stage 2 when ngrok friction starts mattering. Move to Stage 3 when revenue makes the cost trivial.

The point of writing this down now is that you don't have to think about it again until a trigger fires. When one does, this spec is the framework.
