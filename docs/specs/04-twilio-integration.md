# 04 — Twilio Integration

## Purpose of this document

The hard part of this build. Specifies how to wire Twilio for browser-based outbound calling with automatic recording. Includes complete code examples that the Engineer should adapt rather than write from scratch.

## What needs to exist before coding

1. Twilio account (sign up at twilio.com)
2. Account SID and Auth Token (from console)
3. Phone number purchased ($1.15/month, Chicago 312 or 773 area code)
4. API Key + Secret pair created (different from Auth Token, used for token signing)
5. TwiML App created — points to `/api/twilio/voice` on the public tunnel URL (must be HTTPS)
6. ngrok or cloudflared tunnel running, exposing localhost:8000 publicly via HTTPS
7. Composer package installed: `composer require twilio/sdk`

**HTTPS requirement:** Twilio webhooks must use HTTPS URLs. ngrok provides both http:// and https:// — always use the https variant in TwiML App config and recording callbacks. Twilio will reject http:// callbacks.

## CallSid concepts (read this before reading the flow)

There are two related but distinct CallSids in this system:

- **Parent CallSid:** the call between the browser and Twilio (created when `Device.connect()` runs)
- **Child CallSid (DialCallSid):** the call between Twilio and the lead (created when `<Dial>` runs, after Twilio gets our TwiML)

For our purposes:

- The voice TwiML endpoint receives the **parent** CallSid in its `CallSid` parameter
- The recording webhook for `<Dial record="record-from-answer-dual">` also receives the **parent** CallSid
- The two match. We store the parent CallSid in our `calls.twilio_call_sid` column and the recording webhook's `CallSid` parameter looks it up correctly

This is consistent with Twilio's documented behavior for `<Dial>`-initiated dual-channel recordings: the recording is associated with the call leg that contains the `<Dial>` verb (the parent), and the recordingStatusCallback's `CallSid` reflects that.

**If recording webhooks log "unknown call":** something is wrong with this assumption (or the parent SID wasn't saved, or the webhook fired before the voice endpoint completed). To debug:
1. Add `Log::channel('phonebooth_webhooks')->info('Recording webhook params', $request->all())` to the webhook handler (already present in the code below)
2. Make a test call, check the log for the full param payload
3. Compare the `CallSid` value in the webhook against the `twilio_call_sid` column in your `calls` table for the most recent call
4. If they differ, you've found a Twilio behavior I got wrong — update the matching logic

## The flow (with call row association)

```
1. User loads cockpit page
   → Browser GETs /api/twilio/token
   → Laravel signs and returns capability token
   → Browser initializes Twilio.Device with the token

2. User clicks "Call" button
   → Browser POSTs to /calls with { lead_id }
   → Laravel creates Call row, returns { call_id }
   → Browser calls Twilio.Device.connect({ params: { To: "+1...", call_id: "123" } })
   → Twilio receives the connect request, generates a parent CallSid (e.g. CAabc)
   → Twilio POSTs to our /api/twilio/voice with { To, CallSid: CAabc, call_id: 123 }
   → Our voice endpoint:
       - Updates Call row #123 with twilio_call_sid = CAabc
       - Returns TwiML <Dial> with record="record-from-answer-dual"
   → Twilio dials the lead (creates child call CAxyz, but we don't track it)
   → Audio bridges between browser and lead

3. User talks, hangs up
   → Browser fires Twilio.Device.disconnect or remote hangs up
   → Twilio finalizes recording (recording is on the parent leg)
   → Twilio POSTs to /webhooks/twilio/recording with { CallSid: CAabc, RecordingUrl, ... }
   → Webhook finds Call by twilio_call_sid = CAabc, saves recording_url
```

The key insight: passing `call_id` as a custom param through `Twilio.Device.connect()` makes it available to our voice endpoint, which is the only place where we can correlate our internal call row with Twilio's CallSid.

## Code: capability token endpoint

`app/Http/Controllers/TwilioTokenController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Models\Call;
use Illuminate\Http\Request;
use Twilio\Jwt\AccessToken;
use Twilio\Jwt\Grants\VoiceGrant;

class TwilioTokenController extends Controller
{
    public function generate()
    {
        $accountSid = config('services.twilio.account_sid');
        $apiKeySid = config('services.twilio.api_key_sid');
        $apiKeySecret = config('services.twilio.api_key_secret');
        $twimlAppSid = config('services.twilio.twiml_app_sid');

        $identity = 'phonebooth-user';

        $token = new AccessToken(
            $accountSid,
            $apiKeySid,
            $apiKeySecret,
            3600,  // 1 hour
            $identity
        );

        $voiceGrant = new VoiceGrant();
        $voiceGrant->setOutgoingApplicationSid($twimlAppSid);
        $voiceGrant->setIncomingAllow(false);  // outbound-only for Phase 1

        $token->addGrant($voiceGrant);

        return response()->json([
            'token' => $token->toJWT(),
            'identity' => $identity,
        ]);
    }

    public function voice(Request $request)
    {
        $toNumber = $request->input('To');
        $callId = $request->input('call_id');           // custom param from browser
        $twilioCallSid = $request->input('CallSid');    // standard Twilio param (parent)
        $fromNumber = config('services.twilio.phone_number');
        $tunnelUrl = config('app.tunnel_url');

        // Associate our Call row with Twilio's parent CallSid.
        // This is THE moment where the two systems' identifiers get linked.
        // The recording webhook will fire with this same parent CallSid.
        if ($callId && $twilioCallSid) {
            Call::where('id', $callId)->update([
                'twilio_call_sid' => $twilioCallSid,
            ]);
        }

        $twiml = new \Twilio\TwiML\VoiceResponse();
        $dial = $twiml->dial('', [
            'callerId' => $fromNumber,
            'record' => 'record-from-answer-dual',
            'recordingStatusCallback' => $tunnelUrl . '/webhooks/twilio/recording',
            'recordingStatusCallbackMethod' => 'POST',
            'recordingStatusCallbackEvent' => 'completed',
        ]);
        $dial->number($toNumber);

        return response($twiml, 200)->header('Content-Type', 'text/xml');
    }
}
```

## Code: services config

`config/services.php` Twilio block:

```php
'twilio' => [
    'account_sid' => env('TWILIO_ACCOUNT_SID'),
    'auth_token' => env('TWILIO_AUTH_TOKEN'),
    'api_key_sid' => env('TWILIO_API_KEY_SID'),
    'api_key_secret' => env('TWILIO_API_KEY_SECRET'),
    'twiml_app_sid' => env('TWILIO_TWIML_APP_SID'),
    'phone_number' => env('TWILIO_PHONE_NUMBER'),
],
```

`config/app.php` add:
```php
'tunnel_url' => env('TUNNEL_URL', 'http://localhost:8000'),
```

In `.env`, this should be the HTTPS ngrok URL during dev:
```
TUNNEL_URL=https://abc123.ngrok-free.app
```

## CSRF configuration

Twilio POSTs to our voice and webhook endpoints, but Twilio doesn't send CSRF tokens. These routes need CSRF exemption.

`app/Http/Middleware/VerifyCsrfToken.php`:

```php
protected $except = [
    'webhooks/twilio/*',
    'api/twilio/voice',
];
```

**Don't add `calls/*` here.** The browser POSTs to `/calls` and `/calls/{id}` and includes the CSRF token via the `X-CSRF-TOKEN` header. Excluding those routes would defeat CSRF protection on the user-facing endpoints.

The `/api/twilio/token` endpoint is a GET, so CSRF doesn't apply.

## Code: browser-side Twilio.Device wrapper

`resources/js/twilio-device.js`:

```javascript
import { Device } from '@twilio/voice-sdk';

export class PhoneboothDevice {
    constructor() {
        this.device = null;
        this.activeCall = null;
        this.onStatusChange = null;  // callback set by cockpit
    }

    async initialize() {
        const response = await fetch('/api/twilio/token');
        const data = await response.json();

        this.device = new Device(data.token, {
            logLevel: 1,
            codecPreferences: ['opus', 'pcmu'],
        });

        this.device.on('registered', () => this.notify('idle'));
        this.device.on('error', (error) => {
            console.error('Twilio Device error:', error);
            this.notify('error', error);
        });

        await this.device.register();
    }

    /**
     * Place an outbound call.
     * @param {string} phoneNumber - E.164 format, e.g., "+13125551234"
     * @param {number} callId - Our internal Call row ID, passed to TwiML voice endpoint
     */
    async call(phoneNumber, callId) {
        if (!this.device) throw new Error('Device not initialized');

        this.notify('connecting');
        this.activeCall = await this.device.connect({
            params: {
                To: phoneNumber,
                call_id: String(callId),  // Twilio passes this through to our voice endpoint
            },
        });

        this.activeCall.on('accept', () => this.notify('on-call'));
        this.activeCall.on('disconnect', () => {
            this.notify('idle');
            this.activeCall = null;
        });
        this.activeCall.on('cancel', () => {
            this.notify('idle');
            this.activeCall = null;
        });
        this.activeCall.on('reject', () => {
            this.notify('idle');
            this.activeCall = null;
        });

        return this.activeCall;
    }

    hangup() {
        if (this.activeCall) {
            this.activeCall.disconnect();
        }
    }

    notify(status, payload = null) {
        if (this.onStatusChange) {
            this.onStatusChange(status, payload);
        }
    }
}
```

## Code: cockpit page wiring

`resources/js/cockpit.js`:

```javascript
import { PhoneboothDevice } from './twilio-device';

const device = new PhoneboothDevice();
let currentCallId = null;
let timerInterval = null;
let timerStart = null;

// Page elements
const callBtn = document.getElementById('call-btn');
const hangupBtn = document.getElementById('hangup-btn');
const statusEl = document.getElementById('call-status');
const timerEl = document.getElementById('call-timer');
const postCallForm = document.getElementById('post-call-form');
const phoneNumber = callBtn.dataset.phone;
const leadId = callBtn.dataset.leadId;

device.onStatusChange = (status, payload) => {
    statusEl.textContent = status;

    if (status === 'on-call') {
        timerStart = Date.now();
        timerInterval = setInterval(updateTimer, 1000);
        callBtn.style.display = 'none';
        hangupBtn.style.display = 'block';
    } else if (status === 'idle') {
        clearInterval(timerInterval);
        callBtn.style.display = 'block';
        hangupBtn.style.display = 'none';
        if (currentCallId) {
            // Call ended; enable post-call form
            enablePostCallForm();
        }
    } else if (status === 'connecting') {
        callBtn.disabled = true;
    } else if (status === 'error') {
        alert('Call failed: ' + (payload?.message || 'unknown error'));
        callBtn.disabled = false;
    }
};

callBtn.addEventListener('click', async () => {
    // 1. Create call row in DB (CSRF token included as header)
    const response = await fetch('/calls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify({ lead_id: leadId }),
    });

    if (!response.ok) {
        alert('Failed to create call record. Check console.');
        return;
    }

    const data = await response.json();
    currentCallId = data.call_id;

    // 2. Initiate Twilio call. The call_id is passed through Twilio
    //    to our /api/twilio/voice endpoint, which uses it to associate
    //    the Twilio CallSid with our Call row.
    await device.call(phoneNumber, currentCallId);
});

hangupBtn.addEventListener('click', () => {
    device.hangup();
});

function updateTimer() {
    const elapsed = Math.floor((Date.now() - timerStart) / 1000);
    const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const secs = (elapsed % 60).toString().padStart(2, '0');
    timerEl.textContent = `${mins}:${secs}`;
}

function enablePostCallForm() {
    postCallForm.querySelectorAll('input, select, textarea, button').forEach(el => {
        el.disabled = false;
    });
    postCallForm.dataset.callId = currentCallId;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    device.initialize().catch(err => {
        console.error('Failed to initialize Twilio:', err);
        alert('Could not initialize phone. Check console.');
    });
});
```

Make sure the Blade layout includes the CSRF meta tag in `<head>`:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

## Code: webhook signature verification

`app/Http/Middleware/VerifyTwilioSignature.php`:

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Twilio\Security\RequestValidator;

class VerifyTwilioSignature
{
    public function handle($request, Closure $next)
    {
        $validator = new RequestValidator(config('services.twilio.auth_token'));

        $signature = $request->header('X-Twilio-Signature');
        // CRITICAL: this URL must EXACTLY match what Twilio used to call us.
        // If TUNNEL_URL is wrong or stale, signature verification fails
        // even on legitimate requests.
        $url = config('app.tunnel_url') . $request->getPathInfo();
        $params = $request->all();

        if (!$validator->validate($signature, $url, $params)) {
            abort(403, 'Invalid Twilio signature');
        }

        return $next($request);
    }
}
```

Register in `app/Http/Kernel.php` route middleware:
```php
protected $routeMiddleware = [
    // ...
    'twilio.signature' => \App\Http\Middleware\VerifyTwilioSignature::class,
];
```

Apply to webhook routes:
```php
Route::post('/webhooks/twilio/recording', [TwilioWebhookController::class, 'recording'])
    ->middleware('twilio.signature');
```

For local dev, signature verification can be temporarily disabled if the tunnel URL is changing rapidly. **Re-enable before any production exposure.**

## Code: recording webhook

`app/Http/Controllers/TwilioWebhookController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Models\Call;
use App\Services\EventLogger;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class TwilioWebhookController extends Controller
{
    public function recording(Request $request, EventLogger $events)
    {
        // Log full params on every webhook — useful for verifying
        // the parent vs child CallSid behavior described in the spec
        Log::channel('phonebooth_webhooks')->info('Recording webhook received', $request->all());

        $callSid = $request->input('CallSid');
        $recordingUrl = $request->input('RecordingUrl');
        $duration = $request->input('RecordingDuration');

        $call = Call::where('twilio_call_sid', $callSid)->first();

        if (!$call) {
            Log::channel('phonebooth_webhooks')->warning('Recording webhook for unknown call', [
                'sid' => $callSid,
                'all_params' => $request->all(),  // helps debug if SID mismatch
            ]);
            return response('', 200);
        }

        $call->update([
            'recording_url' => $recordingUrl . '.mp3',  // append .mp3 to get audio
            'duration_seconds' => (int) $duration,
            'ended_at' => $call->ended_at ?? now(),
        ]);

        $events->record('twilio_recording_received', 'call', $call->id, [
            'twilio_call_sid' => $callSid,
            'recording_url' => $call->recording_url,
            'duration_seconds' => (int) $duration,
        ]);

        return response('', 200);
    }
}
```

## Setup checklist for the Engineer

In order:

1. [ ] Sign up for Twilio
2. [ ] Buy a Chicago number (312 or 773 area code) — $1.15/month
3. [ ] Note Account SID and Auth Token from console
4. [ ] Create API Key + Secret pair (Console → Account → API keys & tokens → Create API Key)
5. [ ] Install ngrok (`brew install ngrok` or download)
6. [ ] Run `ngrok http 8000` — note the **HTTPS** URL (not http)
7. [ ] Create TwiML App in console pointing Voice URL to `{https-ngrok-url}/api/twilio/voice`
8. [ ] Copy TwiML App SID
9. [ ] Populate `.env` with all six TWILIO_* vars + TUNNEL_URL (https URL)
10. [ ] `composer require twilio/sdk`
11. [ ] `npm install @twilio/voice-sdk`
12. [ ] Build views and JS per spec 03
13. [ ] Test: load cockpit page, check console for "Twilio Device registered"
14. [ ] Test: place a call to your own cell, verify audio works in headset
15. [ ] Test: hang up, watch logs for recording webhook arrival — confirm CallSid in webhook matches twilio_call_sid in `calls` table
16. [ ] Verify recording URL is saved on the call row in SQLite

## Common gotchas

- **Trial accounts can only call verified numbers.** Verify your own cell in Twilio console before testing. Production calling to arbitrary numbers requires upgrading the account ($20 minimum credit).
- **ngrok URL changes on free tier when restarted.** Pin it via paid plan ($8/mo) or use cloudflared free tier (more stable). Update TwiML App webhook + TUNNEL_URL in .env when it changes.
- **Outbound caller ID must match your verified number** in Twilio. The `callerId` in TwiML must be your Twilio-purchased number.
- **Browser will request mic permission** the first time. Permission must be granted or `device.connect()` fails silently.
- **Audio devices on macOS / Windows** sometimes require a page reload after plugging in headset. Twilio.Device caches the audio device list at init.
- **CSRF token handling:** `/calls` and `/calls/*` need it (browser-driven, JS sends header). `/webhooks/twilio/*` and `/api/twilio/voice` need exemption (Twilio-driven, no token).
- **Signature verification fails when TUNNEL_URL doesn't match the actual URL Twilio called.** If you regenerate ngrok, update the env value AND the TwiML App webhook config.
- **Recording URL needs `.mp3` appended** to be playable directly. Twilio returns the URL without extension.
- **The recording is stereo (dual-channel)** with `record-from-answer-dual`. Left channel is your voice, right is theirs. faster-whisper mixes to mono by default.
- **The recording webhook can take 30-90 seconds to fire** after hangup, sometimes longer for long calls. Don't surface a "Process Call" button until the recording arrives.
- **Cancelled calls leave orphan rows.** If user clicks Call then hangs up before Twilio's voice endpoint runs, a Call row exists with no `twilio_call_sid`. These rows can sit forever harmlessly in Phase 1; Phase 2 can clean them up via a scheduled job.

## Cost expectations

At Phase 1 volume (10 calls/day, 5 min average, 22 work days):
- Number rental: $1.15/month
- Outbound minutes: 1,100 × $0.014 = $15.40
- Recording: 1,100 × $0.0025 = $2.75
- Recording storage: ~$0.50
- Total: ~$20/month at moderate volume; ~$5/month if you do 5 calls/day average
