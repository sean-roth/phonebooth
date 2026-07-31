# Output format — Web Development - Master tab

Live sheet: the master lead spreadsheet, tab **"Web Development - Master"**.
Separate tab from the SOPs tracker. Never write to the SOPs tab.

## Columns, in order

```
Source | Trade | Company | Phone | Website | Reviews | Rating |
SiteStatus | Platform | PSI | LCP | MobileOK | TapPhone | HTTPS | GBP |
Observation | Score | ProfileScore | WebsiteScore | BuyerScore | Hook | Contact |
Status | Last Touch | Next Touch | Attempts | Audit Sent | 60-Day Re-dial | Notes |
Tier | Price | Deposit | Balance | Retainer | DocLink | PSILink
```

## Who writes what

This division matters. Writing into a human column is worse than leaving it
empty, because Sean will trust it.

### The agent writes
| Column | Value |
|---|---|
| Source | `Places <corridor> <trade> <date>` |
| Trade | From the sweep slice |
| Company | Places name, cleaned |
| Phone | Places. Never invented. |
| Website | The URL if one exists — **including when it was found by domain guess rather than the profile** |
| Reviews | Count |
| Rating | Average |
| GBP | `Complete` / `Thin` / `Unclaimed` / `Missing` |
| PSI | PageSpeed mobile score, survivors only |
| LCP | Seconds, bare number, survivors only |
| Score | Provisional, from `qualification-prompt.md` |
| ProfileScore | `profile_subscore` from qualify(), uncapped |
| WebsiteScore | `min(website_subscore_raw, 20)` — capped, so ProfileScore + WebsiteScore + BuyerScore == Score reads directly off the sheet |
| BuyerScore | `buyer_subscore` from qualify() |
| Hook | One sentence, data-supported only |
| Status | `Not called` |
| Notes | The model's one-liner, plus the site class |

### The human writes — leave these empty
`SiteStatus`, `Platform`, `MobileOK`, `TapPhone`, `HTTPS`, `Observation`,
`Contact`, `Last Touch`, `Next Touch`, `Attempts`, `Audit Sent`,
`60-Day Re-dial`, `Tier`, `Price`, `Deposit`, `Balance`, `Retainer`, `DocLink`

`Observation` in particular is the human's column. It records what Sean saw
looking at the site and the profile as a customer would. The agent has not
looked. Writing there fabricates a judgment.

`PSILink` is a sheet formula, not an agent field. Do not overwrite it.

## The site class

Every row's `Notes` opens with the class:

```
[SITE_UNLINKED] joheating.com resolves but is absent from the profile.
[SOCIAL_ONLY] Profile links to a Facebook page.
[NO_SITE] No domain found by pattern or search.
[SITE_LINKED] —
```

Sean sorts on this. It is the fastest read on whether a corridor is worth
returning to.

## Sort and delivery

Append highest `Score` first. Rows marked `review` go to the review tab, never
the callable list.

Stop a run at roughly 40 callable rows. Per the ROADMAP anti-goals, sourcing
faster than one caller can dial is wasted compute — and a long list is
demoralizing in a way a short one is not.
