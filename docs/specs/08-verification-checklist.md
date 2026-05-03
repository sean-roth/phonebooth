# 08 — Verification Checklist

## Why this exists

The Designer Claude that wrote specs 04 and 05 worked from training-data memory of Twilio and faster-whisper, **not from current official documentation**. The architecture and flow are sound; specific implementation details (class names, parameter names, exact pricing, feature availability, version requirements) may be stale.

This document lists every specific detail to verify, with the docs URL where to check. The Engineer should work through this during the relevant build steps.

**Note:** an earlier version of this spec also covered the Anthropic Messages API. That section was removed when the architecture pivoted from API-based coaching to Claude Desktop with filesystem MCP (see specs 05 and 09). The dashboard does not call the Anthropic API; verification of API details is no longer needed for Phase 1.

## How to use this

During build:
- **Before step 4 (Twilio infrastructure):** verify the Twilio sections below
- **Before step 6 (Whisper):** verify the faster-whisper section AND the dual-channel splitting section
- **Before step 7 (filesystem MCP setup):** verify the MCP filesystem server documentation (spec 09 has the URL)

When you find something wrong, **fix it in the relevant spec file and commit**. Future Claudes (and your future self) will work from the verified version. A wrong API detail discovered at hour 3 of build is much cheaper to fix than at hour 8.

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

If custom params are NOT passed through to the voice endpoint, the call_id flow in spec 04 won't work. This is the single most important Twilio detail to verify.

## Twilio: TwiML `<Dial>` and recording

**Docs:** https://www.twilio.com/docs/voice/twiml/dial

- [ ] `<Dial>` `record` attribute supports value `record-from-answer-dual` for dual-channel recording
- [ ] `recordingStatusCallback` attribute on `<Dial>` for the webhook URL
- [ ] `recordingStatusCallbackMethod` and `recordingStatusCallbackEvent` attributes
- [ ] `callerId` attribute for setting outbound caller ID
- [ ] **The dual-channel format is genuinely stereo** (not stereo-encoded mono). Verify by testing — the spec 05 channel-splitting workflow depends on the recording having distinct left and right audio.

## Twilio: Recording webhook

**Docs:** https://www.twilio.com/docs/voice/api/recording#http-status-callbacks-recording-resource

- [ ] **Verify which CallSid the webhook actually sends.** Check Twilio's docs and explicitly confirm whether it's the parent or child for `<Dial>`-initiated dual-channel recordings.
- [ ] Other parameters: `RecordingSid`, `RecordingUrl`, `RecordingDuration`, `RecordingStatus`, `RecordingChannels`, `RecordingStartTime`
- [ ] Whether `ParentCallSid` is also included as a separate parameter
- [ ] Whether the `RecordingUrl` requires `.mp3` appended for direct playback
- [ ] HTTPS requirement for callback URLs
- [ ] Twilio's retry behavior on non-200 webhook responses

If the webhook actually sends the *child* CallSid: spec 04's matching logic needs to change.

If the webhook sends both via `ParentCallSid`: simpler — match either.

## Twilio: Recording deletion API

**Docs:** https://www.twilio.com/docs/voice/api/recording#delete-a-recording-resource

This is needed for spec 10's auto-delete-on-decline behavior.

- [ ] DELETE endpoint format: `DELETE /2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid}.json`
- [ ] Authentication uses basic auth with Account SID + Auth Token
- [ ] Successful deletion returns 204 No Content
- [ ] Whether deletion is permanent or moves to soft-deleted state
- [ ] Whether the recording-storage billing stops at deletion or continues until end of billing period

If the endpoint format differs, update spec 03's `deleteRecording()` method.

## Twilio: Webhook signature verification

**Docs:** https://www.twilio.com/docs/usage/webhooks/webhooks-security

- [ ] `X-Twilio-Signature` header is the signature
- [ ] Validation uses Auth Token (not API Key Secret)
- [ ] URL passed to validator must include scheme + full path (no trailing slash unless the actual URL has one)
- [ ] Whether body params are included in signature computation for POST webhooks (they are, but verify)

Common gotcha: if your reverse proxy or tunnel rewrites the URL, the URL you pass to the validator must match what Twilio used.

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
- [ ] Approximate speed on CPU for `small` model

The faster-whisper API is fairly stable but the segments iterator behavior or kwarg names may have evolved.

## Dual-channel splitting via ffmpeg

This is new in the updated spec 05 (channels are split separately and transcribed in two passes for speaker attribution).

- [ ] ffmpeg `-map_channel` syntax produces clean mono output files
- [ ] Verify with `ffprobe`: output should report `channels=1` for both split files
- [ ] If `-map_channel` doesn't work, alternative is `-af "pan=mono|c0=c0"` and `-af "pan=mono|c0=c1"`
- [ ] ffmpeg version on the OptiPlex (some older versions handle channel mapping differently)

The splitting test in spec 05's "First-run notes" verifies this end-to-end. Run that test before processing real call audio.

## ngrok

**Docs:** https://ngrok.com/docs

- [ ] Free tier provides HTTPS URLs
- [ ] Free tier URL rotates on every restart (confirm — there may be free static URLs now)
- [ ] Paid tier pricing for static URL ($8/mo cited in spec)
- [ ] cloudflared as a free alternative still exists and works similarly

If cloudflared has changed or ngrok has free static URLs now, update spec 04.

## Things the Designer assumed about Sean's environment

- [ ] Python 3.10+ on the OptiPlex
- [ ] ffmpeg installed (`which ffmpeg`)
- [ ] Node.js / npm version compatible with current `@twilio/voice-sdk`
- [ ] PHP version compatible with current Laravel (Laravel 11 needs PHP 8.2+; Laravel 12 needs PHP 8.3+)
- [ ] Composer is installed and current
- [ ] Sufficient disk for recordings (~1MB/minute, 220 calls/month × 5min × 1MB = ~1.1GB/month before any deletion)

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
2. **Parent vs child CallSid in recording webhook** — if wrong, recording webhook never matches a call row
3. **Recording deletion API endpoint format** — the spec 10 auto-delete depends on this
4. **ffmpeg `-map_channel` syntax** — if wrong, dual-channel attribution fails (silently in some cases)
5. **Twilio PHP SDK class names** — if namespaces have changed, voice endpoint won't compile
6. **faster-whisper transcribe() return shape** — if segments aren't iterable with .start/.end/.text, the script breaks

Items 1, 2, 3, and 4 are high-impact for Phase 1 working at all. Verify those first.

## What this verification cannot tell you

This checklist verifies APIs against current documentation. It does not verify:

- Whether the architectural decisions are sound (that's spec 01 + design conversation territory)
- Whether the legal compliance approach in spec 10 is correct for Sean's use case (that needs an attorney)
- Whether the coaching framework in `docs/skills/01-jeb-blount.md` actually produces useful coaching (that needs field testing)
- Whether the cockpit UI is usable under stress (that needs Sean using it Monday)
