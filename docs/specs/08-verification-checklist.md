# 08 — Verification Checklist

## Why this exists

The Designer Claude that wrote specs 01-07 worked from training-data memory of Twilio, Anthropic, faster-whisper, and ngrok — **not from current official documentation**. The web_fetch tool was unavailable at the end of the design conversation when this gap was identified, so verification was deferred to the Engineer.

This means specific API details (class names, parameter names, exact pricing, feature availability, version requirements) in specs 04 and 05 may be stale or wrong. The overall architecture and flow are sound; it's the implementation-level details that need confirmation.

This document lists every specific detail to verify, with the docs URL where to check. The Engineer should work through this during the relevant build steps.

## How to use this

During build:
- **Before step 4 (Twilio infrastructure):** verify the Twilio sections below
- **Before step 6 (Whisper):** verify the faster-whisper section
- **Before step 7 (Coaching):** verify the Anthropic Messages API section

When you find something wrong, **fix it in the relevant spec file and commit**. Future Claudes (and your future self) will work from the verified version. A wrong API detail discovered at hour 3 of build is much cheaper to fix than at hour 8.

If anything has changed materially (e.g., entirely new SDK, breaking API change), update both the spec and any references in spec 00 (build order). Add a note in the commit message: "Verified against docs YYYY-MM-DD."

## Twilio: account, numbers, pricing

**Docs:** https://www.twilio.com/docs

- [ ] Trial accounts can only call **verified** numbers (verify your cell)
- [ ] Verified caller ID rule (outbound caller ID must match a Twilio-purchased or verified number)
- [ ] Chicago local number (312 or 773 area code) availability and current monthly cost
- [ ] Outbound minute rate (~$0.014/min, may have changed)
- [ ] Recording per-minute add-on (~$0.0025/min, may have changed)
- [ ] Recording storage cost (~$0.0005/min/month)
- [ ] Inbound minute rate (~$0.0085/min)
- [ ] Trial credit allowance / minimum upgrade balance ($20)
- [ ] Whether SMS A2P registration is required for outbound texting (it is — but the cost ($19.50 one-time + $1.50-3/mo) may have changed)

If pricing has shifted significantly, update the cost expectations in spec 04 and the architecture cost summary in spec 01.

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

The biggest risk: the SDK could have been refactored into a different namespace structure. If the class names don't match, find the current ones and update spec 04's code samples.

## Twilio: Voice JS SDK

**Docs:** https://www.twilio.com/docs/voice/sdks/javascript
**Package:** https://www.npmjs.com/package/@twilio/voice-sdk

- [ ] Package name `@twilio/voice-sdk` is current (this replaced the older `twilio-client` package)
- [ ] `Device` class import: `import { Device } from '@twilio/voice-sdk'`
- [ ] `Device` constructor accepts `(token, options)` with `logLevel` and `codecPreferences` options
- [ ] `Device.register()` exists and is required before placing calls
- [ ] `Device.connect({ params: {...} })` returns a `Call` object (Promise-wrapped)
- [ ] **Custom params in `Device.connect()` are passed to the TwiML voice URL as POST form data** — this is the load-bearing assumption for the call_id flow
- [ ] `Device` events: `registered`, `error`
- [ ] `Call` events: `accept`, `disconnect`, `cancel`, `reject`
- [ ] `Call.disconnect()` for hanging up

If custom params are NOT passed through to the voice endpoint, the call_id race condition fix in spec 04 won't work. This is the single most important Twilio detail to verify.

Alternative if custom params don't work: associate by phone number + recent timestamp, or use the Twilio API's calls.create() server-side instead of the browser SDK.

## Twilio: TwiML `<Dial>` and recording

**Docs:** https://www.twilio.com/docs/voice/twiml/dial

- [ ] `<Dial>` `record` attribute supports value `record-from-answer-dual` for dual-channel recording
- [ ] `recordingStatusCallback` attribute on `<Dial>` for the webhook URL
- [ ] `recordingStatusCallbackMethod` and `recordingStatusCallbackEvent` attributes
- [ ] `callerId` attribute for setting outbound caller ID

## Twilio: Recording webhook

**Docs:** https://www.twilio.com/docs/voice/api/recording#http-status-callbacks-recording-resource

This is the most important section to verify. Spec 04 makes a specific claim about which CallSid the webhook receives:

> The recording webhook for `<Dial record="record-from-answer-dual">` receives the **parent** CallSid (the call between browser and Twilio), not the child CallSid (the call between Twilio and the lead).

- [ ] **Verify which CallSid the webhook actually sends.** Check Twilio's docs for the parameters list and explicitly confirm whether it's the parent or child for `<Dial>`-initiated dual-channel recordings.
- [ ] Other parameters: `RecordingSid`, `RecordingUrl`, `RecordingDuration`, `RecordingStatus`, `RecordingChannels`, `RecordingStartTime`
- [ ] Whether `ParentCallSid` is also included as a separate parameter
- [ ] Whether the `RecordingUrl` requires `.mp3` appended for direct playback (or some other format)
- [ ] HTTPS requirement for callback URLs
- [ ] Twilio's retry behavior on non-200 webhook responses

If the webhook actually sends the *child* CallSid: spec 04's matching logic needs to change. The voice TwiML endpoint would need to be replaced with an `action` callback on `<Dial>` that fires when the dial completes (with `DialCallSid`), and the voice endpoint would just associate the parent. Two-step linking.

If the webhook sends both via `ParentCallSid`: simpler — match either.

The build-step-4 setup checklist already includes "confirm CallSid in webhook matches twilio_call_sid in calls table." If that confirmation fails, this is where to debug.

## Twilio: Webhook signature verification

**Docs:** https://www.twilio.com/docs/usage/webhooks/webhooks-security

- [ ] `X-Twilio-Signature` header is the signature
- [ ] Validation uses Auth Token (not API Key Secret)
- [ ] URL passed to validator must include scheme + full path (no trailing slash unless the actual URL has one)
- [ ] Whether body params are included in signature computation for POST webhooks (they are, but verify)

Common gotcha: if your reverse proxy or tunnel rewrites the URL (e.g., adds/removes a port), the URL you pass to the validator must match what Twilio used. ngrok preserves the URL but it's worth confirming.

## Anthropic: Messages API

**Docs:** https://docs.claude.com/en/api/messages
**Models doc:** https://docs.claude.com/en/docs/about-claude/models/all-models

- [ ] Endpoint: `https://api.anthropic.com/v1/messages`
- [ ] Required headers: `x-api-key`, `anthropic-version`, `content-type`
- [ ] Current `anthropic-version` to use (spec uses `2023-06-01` — still supported but may not be current best practice)
- [ ] Request body shape: `model`, `max_tokens`, `messages` (array of `{role, content}`)
- [ ] Response shape: `content[0].text` for the text response
- [ ] Current Sonnet model identifier (spec uses `claude-sonnet-4-6`)
- [ ] Current Sonnet pricing per million input/output tokens (spec assumes $3/M in, $15/M out)
- [ ] Whether prompt caching could reduce costs for the repeated skill prompt content (would be a Phase 2 optimization)
- [ ] Rate limits at the spec's projected volume (~10-30 calls per day, well under any tier)

If pricing is wrong: update `EventLogger::recordCoaching()` cost calculation in spec 07.
If model string is wrong: update `services.anthropic.model` default in spec 05.
If response shape is different: update `CoachingGenerator::generate()` parsing in spec 05.

## faster-whisper

**Docs:** https://github.com/SYSTRAN/faster-whisper
**PyPI:** https://pypi.org/project/faster-whisper/

- [ ] Install command: `pip install faster-whisper`
- [ ] Class `WhisperModel` with constructor `(model_size, device, compute_type)`
- [ ] Constructor params: `device` accepts `cpu` / `cuda`; `compute_type` accepts `int8` / `float16` / etc.
- [ ] `model.transcribe(audio_path, **kwargs)` returns `(segments, info)`
- [ ] Each segment has `.start`, `.end`, `.text` attributes
- [ ] `language` kwarg: passing `None` or omitting it triggers auto-detection
- [ ] `vad_filter` kwarg for voice activity detection
- [ ] `beam_size` kwarg
- [ ] Memory requirements for `small` model on int8 (~1.5GB)
- [ ] Whether it requires ffmpeg installed system-wide (yes, but confirm)
- [ ] Default model download location (`~/.cache/huggingface/`)
- [ ] Approximate speed on CPU for `small` model (real-world benchmarks may differ from spec estimates)

The faster-whisper API is fairly stable but the segments iterator behavior or kwarg names may have evolved.

## ngrok

**Docs:** https://ngrok.com/docs

- [ ] Free tier provides HTTPS URLs (it does, but confirm)
- [ ] Free tier URL rotates on every restart (confirm — there may be free static URLs now)
- [ ] Paid tier pricing for static URL ($8/mo cited in spec)
- [ ] cloudflared as a free alternative still exists and works similarly

If cloudflared has changed or ngrok has free static URLs now, update spec 04.

## Things the Designer assumed about Sean's environment

These weren't checked; the Engineer can confirm:

- [ ] Python 3.10+ on the OptiPlex (Sean uses it for Clara work, should be there)
- [ ] ffmpeg installed (`which ffmpeg`)
- [ ] Node.js / npm version compatible with current `@twilio/voice-sdk`
- [ ] PHP version compatible with current Laravel (Laravel 11 needs PHP 8.2+; Laravel 12 needs PHP 8.3+)
- [ ] Composer is installed and current
- [ ] Sufficient disk for recordings (calls accumulate — at ~1MB/minute, 220 calls/month × 5min × 1MB = ~1.1GB/month)

## Quick verification template

For each section above, the verification flow is:

1. Open the docs URL
2. Read for ~3-5 minutes, comparing to the relevant spec section
3. If everything matches: check the boxes, move on
4. If something's wrong: fix the spec file, commit with message referencing this checklist
5. If something's MAJORLY wrong (architectural assumption broken): pause and surface it before continuing

Don't skip this. The Designer Claude was confident-sounding but working from memory. Trust the docs.

## What the Designer is most uncertain about

In rough order of "if this is wrong it would hurt the most":

1. **Voice JS SDK custom params propagation to TwiML voice endpoint** — the entire call_id flow depends on this
2. **Parent vs child CallSid in recording webhook** — if wrong, recording webhook never matches a call row
3. **Anthropic API response shape** — if `content[0].text` isn't right, coaching saves empty
4. **Twilio PHP SDK class names** — if namespaces have changed, voice endpoint won't compile
5. **Anthropic Sonnet model string** — if `claude-sonnet-4-6` is wrong or deprecated, API returns 404
6. **faster-whisper transcribe() return shape** — if segments aren't iterable with .start/.end/.text, the script breaks

Items 1, 2, and 3 are existential to the Phase 1 system working at all. Verify those first.
