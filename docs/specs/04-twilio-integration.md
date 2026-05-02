# 04 — Twilio Integration

## Purpose of this document

The hard part of this build. Specifies how to wire Twilio for browser-based outbound calling with automatic recording. Includes complete code examples that the Engineer should adapt rather than write from scratch.

## What needs to exist before coding

1. Twilio account (sign up at twilio.com)
2. Account SID and Auth Token (from console)
3. Phone number purchased ($1.15/month, Chicago 312 or 773 area code)
4. API Key + Secret pair created (different from Auth Token, used for token signing)
5. TwiML App created — points to `/api/twilio/voice` on the public tunnel URL
6. ngrok or cloudflared tunnel running, exposing localhost:8000 publicly
7. Composer package installed: `composer require twilio/sdk`

## The flow

```
1. User loads cockpit page
   → Browser requests /api/twilio/token
   → Laravel signs and returns capability token
   → Browser initializes Twilio.Device with the token

2. User clicks "Call" button
   → Browser calls Twilio.Device.connect({ params: { To: "+13125551234" } })
   → Twilio receives the connect request
   → Twilio POSTs to our /api/twilio/voice (TwiML App webhook URL)
   → Our endpoint returns TwiML <Dial> with record="record-from-answer-dual"
   → Twilio dials the lead, bridges audio with the browser

3. User talks, hangs up
   → Browser fires Twilio.Device.disconnect or remote hangs up
   → Twilio finalizes recording
   → Twilio POSTs to /webhooks/twilio/recording with recording URL

4. Laravel saves recording_url on the call row
```

## Code: capability token endpoint

`app/Http/Controllers/TwilioTokenController.php`:

```php
<?php

namespace App\Http\Controllers;

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
        $fromNumber = config('services.twilio.phone_number');
        $tunnelUrl = config('app.tunnel_url');  // e.g., https://abc123.ngrok.io

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

`config/services.twilio` block:

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

    async call(phoneNumber) {
        if (!this.device) throw new Error('Device not initialized');

        this.notify('connecting');
        this.activeCall = await this.device.connect({
            params: { To: phoneNumber },
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
    // 1. Create call row in DB
    const response = await fetch('/calls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify({ lead_id: leadId }),
    });
    const data = await response.json();
    currentCallId = data.call_id;

    // 2. Initiate Twilio call
    await device.call(phoneNumber);
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
        $url = config('app.tunnel_url') . $request->getPathInfo();
        $params = $request->all();

        if (!$validator->validate($signature, $url, $params)) {
            abort(403, 'Invalid Twilio signature');
        }

        return $next($request);
    }
}
```

Apply to webhook routes via route middleware:
```php
Route::post('/webhooks/twilio/recording', [TwilioWebhookController::class, 'recording'])
    ->middleware('twilio.signature');
```

## Code: recording webhook

`app/Http/Controllers/TwilioWebhookController.php`:

```php
public function recording(Request $request)
{
    $callSid = $request->input('CallSid');
    $recordingUrl = $request->input('RecordingUrl');
    $duration = $request->input('RecordingDuration');

    $call = Call::where('twilio_call_sid', $callSid)->first();

    if (!$call) {
        Log::warning('Recording webhook for unknown call', ['sid' => $callSid]);
        return response('', 200);
    }

    $call->update([
        'recording_url' => $recordingUrl . '.mp3',  // append .mp3 to get audio
        'duration_seconds' => (int) $duration,
        'ended_at' => $call->ended_at ?? now(),
    ]);

    return response('', 200);
}
```

## Setup checklist for the Engineer

In order:

1. [ ] Sign up for Twilio (use the user's email)
2. [ ] Buy a Chicago number (312 or 773 area code) — $1.15/month
3. [ ] Note Account SID and Auth Token from console
4. [ ] Create API Key + Secret pair (Console → Account → API keys & tokens → Create API Key)
5. [ ] Install ngrok (`brew install ngrok` or download)
6. [ ] Run `ngrok http 8000` — note the HTTPS URL
7. [ ] Create TwiML App in console pointing Voice URL to `{ngrok-url}/api/twilio/voice`
8. [ ] Copy TwiML App SID
9. [ ] Populate `.env` with all six TWILIO_* vars + TUNNEL_URL
10. [ ] `composer require twilio/sdk`
11. [ ] `npm install @twilio/voice-sdk` (note: this is the modern SDK, not the legacy `twilio-client`)
12. [ ] Build views and JS per spec 03
13. [ ] Test: load cockpit page, check console for "Twilio Device registered"
14. [ ] Test: place a call to your own cell, verify audio works in headset
15. [ ] Test: hang up, watch logs for recording webhook arrival
16. [ ] Verify recording URL is saved on the call row in SQLite

## Common gotchas

- **ngrok URL changes on free tier when restarted.** Pin it via paid plan ($8/mo) or use cloudflared free tier (more stable). Update TwiML App webhook + TUNNEL_URL when it changes.
- **Outbound caller ID must match your verified number** in Twilio. Trial accounts can only call verified numbers — verify your cell in Twilio console for testing.
- **Browser will request mic permission** the first time. Permission must be granted or `device.connect()` fails silently.
- **Audio devices on macOS / Windows** sometimes require a page reload after plugging in headset. Twilio.Device caches the audio device list at init.
- **CSRF token** must be included in any POST from the browser (Laravel's default). Either include it in headers (as shown) or exclude `/calls` and `/calls/*` from CSRF in `VerifyCsrfToken`.
- **Recording URL needs `.mp3` appended** to be playable directly. Twilio returns the URL without extension; append it for `<audio src=>` tags.
- **The recording is stereo (dual-channel)** with `record-from-answer-dual`. Left channel is your voice, right is theirs. faster-whisper handles this fine.

## Cost expectations

At Phase 1 volume (10 calls/day, 5 min average, 22 work days):
- Number rental: $1.15/month
- Outbound minutes: 1,100 × $0.014 = $15.40
- Recording: 1,100 × $0.0025 = $2.75
- Recording storage: ~$0.50
- Total: ~$20/month at moderate volume; ~$5/month if you do 5 calls/day average
