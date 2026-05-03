# 08 — Verification Checklist

## Why this exists

The Designer Claude that wrote spec 04 worked from training-data memory of Twilio's APIs, **not from current official documentation**. The architecture and flow are sound; specific implementation details (class names, parameter names, exact pricing, feature availability, version requirements) may be stale.

This document lists every specific detail to verify, with the docs URL where to check. The Engineer should work through this during build step 4.

**Note: this spec was simplified by spec 11 (recording pivot).** Earlier drafts also covered the Anthropic Messages API, faster-whisper, ffmpeg dual-channel splitting, and Twilio's recording deletion endpoint. Those sections were removed because the architecture no longer involves recording, transcription, or API calls. What remains is the Twilio dialer infrastructure.

## How to use this

During build step 4 (Twilio infrastructure):
- Work through the Twilio sections below before writing code
- When you find something wrong, fix it in the relevant spec file and commit

A wrong API detail discovered at hour 3 of build is much cheaper to fix than at hour 8.

## Twilio: account, numbers, pricing

**Docs:** https://www.twilio.com/docs

- [ ] Trial accounts can only call **verified** numbers
- [ ] Verified caller ID rule (outbound caller ID must match a Twilio-purchased or verified number)
- [ ] Chicago local number (312 or 773 area code) availability and current monthly cost
- [ ] Outbound minute rate (~$0.014/min, may have changed)
- [ ] Inbound minute rate (~$0.0085/min — not used in Phase 1, but verify in case status callbacks count)
- [ ] Trial credit allowance / minimum upgrade balance ($20)

If pricing has shifted, update the cost expectations in spec 04 and spec 01.

## Twilio: PHP SDK

**Docs:** https://www.twilio.com/docs/libraries/reference/twilio-php/
**Composer:** https://packagist.org/packages/twilio/sdk

- [ ] `composer require twilio/sdk` is the correct package
- [ ] Class `Twilio\Jwt\AccessToken` exists with constructor signature `(accountSid, apiKeySid, apiKeySecret, ttl, identity)`
- [ ] Class `Twilio\Jwt\Grants\VoiceGrant` exists with methods `setOutgoingApplicationSid()`, `setIncomingAllow()`
- [ ] `AccessToken::addGrant()` and `toJWT()` methods
- [ ] Class `Twilio\TwiML\VoiceResponse` and `dial()` method signature
- [ ] `Dial->number()` for adding the called number
- [ ] Class `Twilio\Security\RequestValidator` for webhook signature verification
- [ ] `RequestValidator::validate($signature, $url, $params)` signature

The biggest risk: the SDK could have been refactored into a different namespace structure.

## Twilio: Voice JS SDK

**Docs:** https://www.twilio.com/docs/voice/sdks/javascript
**Package:** https://www.npmjs.com/package/@twilio/voice-sdk

- [ ] Package name `@twilio/voice-sdk` is current (this replaced the older `twilio-client`)
- [ ] `Device` class import: `import { Device } from '@twilio/voice-sdk'`
- [ ] `Device` constructor accepts `(token, options)` with `logLevel` and `codecPreferences` options
- [ ] `Device.register()` exists and is required before placing calls
- [ ] `Device.connect({ params: {...} })` returns a `Call` object (Promise-wrapped)
- [ ] **Custom params in `Device.connect()` are passed to the TwiML voice URL as POST form data** — this is the load-bearing assumption for the call_id flow
- [ ] `Device` events: `registered`, `error`
- [ ] `Call` events: `accept`, `disconnect`, `cancel`, `reject`
- [ ] `Call.disconnect()` for hanging up

If custom params are NOT passed through, the call_id flow won't work. This is the single most important Twilio detail to verify.

## Twilio: TwiML `<Dial>`

**Docs:** https://www.twilio.com/docs/voice/twiml/dial

- [ ] `<Dial>` `callerId` attribute for setting outbound caller ID
- [ ] No recording attributes are used in Phase 1 — but if you want to verify they could be re-enabled in Phase 2, check `record="record-from-answer-dual"` exists

The TwiML in spec 04 is intentionally minimal: just a dial with caller ID. No recording, no callbacks, no transcription.

## Twilio: Status webhook

**Docs:** https://www.twilio.com/docs/voice/api/status-callback

- [ ] Status webhook receives `CallSid`, `CallStatus`, `CallDuration`
- [ ] Possible `CallStatus` values: `queued`, `ringing`, `in-progress`, `completed`, `busy`, `failed`, `no-answer`, `canceled`
- [ ] Twilio's retry behavior on non-200 webhook responses

## Twilio: Webhook signature verification

**Docs:** https://www.twilio.com/docs/usage/webhooks/webhooks-security

- [ ] `X-Twilio-Signature` header is the signature
- [ ] Validation uses Auth Token (not API Key Secret)
- [ ] URL passed to validator must include scheme + full path
- [ ] Whether body params are included in signature computation for POST webhooks

Common gotcha: if your reverse proxy or tunnel rewrites the URL, the URL you pass to the validator must match what Twilio used.

## ngrok

**Docs:** https://ngrok.com/docs

- [ ] Free tier provides HTTPS URLs
- [ ] Free tier URL rotates on every restart
- [ ] Paid tier pricing for static URL ($8/mo cited in spec)
- [ ] cloudflared as a free alternative still exists

## Things the Designer assumed about Sean's environment

- [ ] Node.js / npm version compatible with current `@twilio/voice-sdk`
- [ ] PHP version compatible with current Laravel (Laravel 11 needs PHP 8.2+; Laravel 12 needs PHP 8.3+)
- [ ] Composer is installed and current

Note: Python and ffmpeg are no longer required (no Whisper transcription pipeline).

## Quick verification template

For each section above:

1. Open the docs URL
2. Read for ~3-5 minutes, comparing to the relevant spec section
3. If everything matches: check the boxes, move on
4. If something's wrong: fix the spec file, commit
5. If something's MAJORLY wrong (architectural assumption broken): pause and surface it before continuing

Don't skip this. The Designer Claude was confident-sounding but working from memory. Trust the docs.

## What the Designer is most uncertain about

In rough order of "if this is wrong it would hurt the most":

1. **Voice JS SDK custom params propagation to TwiML voice endpoint** — the entire call_id flow depends on this
2. **Twilio PHP SDK class names** — if namespaces have changed, voice endpoint won't compile
3. **Status webhook parameter format** — if `CallDuration` isn't sent or has a different name, duration tracking breaks

Items 1 and 2 are existential to the Phase 1 system working at all. Verify those first.

## What this verification cannot tell you

This checklist verifies APIs against current documentation. It does not verify:

- Whether the architectural decisions are sound (that's spec 01 + design conversation territory)
- Whether the cockpit UI is usable under stress (that needs Sean using it Monday)
- Whether the cold-call-vs-discovery-call coaching split is the right one (that needs field testing — see spec 11 for the rationale)
