# 04 — Twilio Integration

> ⚠️ **VERIFY BEFORE BUILDING**
>
> The code samples in this spec were written from training-data memory of Twilio's APIs, not from current official docs.
>
> Before relying on any specific class name, parameter, or API behavior in this document, work through the Twilio sections of **spec 08 (verification-checklist.md)**.
>
> The two highest-stakes things to verify first:
> 1. Voice JS SDK custom params propagate to the TwiML voice endpoint (call_id flow depends on this)
> 2. PHP SDK class names and namespaces (`Twilio\Jwt\AccessToken`, `Twilio\TwiML\VoiceResponse`)

**Note: this spec was substantially simplified by spec 11 (recording pivot).** Earlier drafts included recording configuration on the TwiML `<Dial>` element, a recording webhook handler, signature verification on the recording webhook, and recording-related cost figures. All of that was removed when the architecture stopped recording cold calls.

## Purpose of this document

How to wire Twilio for browser-based outbound calling. Includes complete code examples that the Engineer should adapt rather than write from scratch.

## What needs to exist before coding

1. Twilio account
2. Account SID and Auth Token (from console)
3. Phone number purchased ($1.15/month, Chicago 312 or 773 area code)
4. API Key + Secret pair created (different from Auth Token, used for token signing)
5. TwiML App created — points to `/api/twilio/voice` on the public tunnel URL (must be HTTPS)
6. ngrok or cloudflared tunnel running, exposing localhost:8000 publicly via HTTPS
7. Composer package installed: `composer require twilio/sdk`

**HTTPS requirement:** Twilio webhooks must use HTTPS URLs. ngrok provides both http:// and https:// — always use the https variant.

## The flow (no recording)

```
1. User loads cockpit page
   → Browser GETs /api/twilio/token
   → Laravel signs and returns capability token
   → Browser initializes Twilio.Device with the token

2. User clicks "Call" button
   → Browser POSTs to /calls with { lead_id }
   → Laravel creates Call row, returns { call_id }
   → Browser calls Twilio.Device.connect({ params: { To: "+1...", call_id: "123" } })
   → Twilio receives the connect request, generates a parent CallSid
   → Twilio POSTs to our /api/twilio/voice with { To, CallSid, call_id }
   → Our voice endpoint:
       - Updates Call row #123 with twilio_call_sid
       - Returns TwiML <Dial> WITHOUT recording attributes
   → Twilio dials the lead
   → Audio bridges between browser and lead

3. User talks, hangs up
   → Browser fires Twilio.Device.disconnect or remote hangs up
   → No recording, no webhook, no follow-up processing
   → User fills in post-call form, saves
```

The system is intentionally simpler than earlier drafts: the call happens, Sean takes notes, the system stores the lead-call relationship and Sean's observations.

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
        $voiceGrant->setIncomingAllow(false);

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
        $twilioCallSid = $request->input('CallSid');    // standard Twilio param
        $fromNumber = config('services.twilio.phone_number');

        // Associate our Call row with Twilio's CallSid
        if ($callId && $twilioCallSid) {
            Call::where('id', $callId)->update([
                'twilio_call_sid' => $twilioCallSid,
            ]);
        }

        $twiml = new \Twilio\TwiML\VoiceResponse();
        $dial = $twiml->dial('', [
            'callerId' => $fromNumber,
            // No record, recordingStatusCallback, etc. per spec 11.
        ]);
        $dial->number($toNumber);

        return response($twiml, 200)->header('Content-Type', 'text/xml');
    }
}
```

Compare to earlier drafts: the `record`, `recordingStatusCallback`, `recordingStatusCallbackMethod`, `recordingStatusCallbackEvent` attributes are gone. The `<Dial>` is a clean dial with no recording.

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

`config/app.php`:
```php
'tunnel_url' => env('TUNNEL_URL', 'http://localhost:8000'),
```

## CSRF configuration

Twilio doesn't send CSRF tokens. Exempt:

```php
protected $except = [
    'webhooks/twilio/*',
    'api/twilio/voice',
];
```

## Code: browser-side Twilio.Device wrapper

`resources/js/twilio-device.js`:

```javascript
import { Device } from '@twilio/voice-sdk';

export class PhoneboothDevice {
    constructor() {
        this.device = null;
        this.activeCall = null;
        this.onStatusChange = null;
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

    async call(phoneNumber, callId) {
        if (!this.device) throw new Error('Device not initialized');

        this.notify('connecting');
        this.activeCall = await this.device.connect({
            params: {
                To: phoneNumber,
                call_id: String(callId),
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

document.addEventListener('DOMContentLoaded', () => {
    device.initialize().catch(err => {
        console.error('Failed to initialize Twilio:', err);
        alert('Could not initialize phone. Check console.');
    });
});
```

CSRF meta tag in `<head>`:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

## Status webhook (optional but recommended)

`app/Http/Controllers/TwilioWebhookController.php`:

```php
<?php

namespace App\Http\Controllers;

use App\Models\Call;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class TwilioWebhookController extends Controller
{
    public function status(Request $request)
    {
        Log::channel('phonebooth_webhooks')->info('Status webhook', $request->all());

        $callSid = $request->input('CallSid');
        $callStatus = $request->input('CallStatus');

        $call = Call::where('twilio_call_sid', $callSid)->first();
        if (!$call) {
            return response('', 200);
        }

        if ($callStatus === 'completed') {
            $call->update([
                'ended_at' => $call->ended_at ?? now(),
                'duration_seconds' => (int) $request->input('CallDuration', 0),
            ]);
        }

        return response('', 200);
    }
}
```

The recording webhook handler that existed in earlier drafts is removed entirely.

## Webhook signature verification

For the status webhook only (no recording webhook to verify):

```php
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

Apply only to status webhook:
```php
Route::post('/webhooks/twilio/status', [TwilioWebhookController::class, 'status'])
    ->middleware('twilio.signature');
```

## Setup checklist for the Engineer

In order:

1. [ ] **Work through the Twilio sections of spec 08 (verification checklist) FIRST**
2. [ ] Sign up for Twilio
3. [ ] Buy a Chicago number — verify current price
4. [ ] Note Account SID and Auth Token from console
5. [ ] Create API Key + Secret pair
6. [ ] Install ngrok (`brew install ngrok` or download)
7. [ ] Run `ngrok http 8000` — note the **HTTPS** URL
8. [ ] Create TwiML App pointing Voice URL to `{https-ngrok-url}/api/twilio/voice`
9. [ ] Copy TwiML App SID
10. [ ] Populate `.env` with all six TWILIO_* vars + TUNNEL_URL (https URL)
11. [ ] `composer require twilio/sdk`
12. [ ] `npm install @twilio/voice-sdk`
13. [ ] Build views and JS per spec 03
14. [ ] Test: load cockpit, console shows "Twilio Device registered"
15. [ ] Test: place a call to your own cell, verify audio works
16. [ ] Test: hang up, verify status webhook fires (optional)

## Common gotchas

- **Trial accounts can only call verified numbers.** Verify your own cell before testing. Production calling requires upgrading the account ($20 minimum credit — verify current).
- **ngrok URL changes on free tier when restarted.** Pin via paid plan ($8/mo) or use cloudflared. Update TwiML App webhook + TUNNEL_URL when it changes.
- **Outbound caller ID must match your verified/purchased Twilio number.**
- **Browser will request mic permission** the first time. Permission must be granted or `device.connect()` fails silently.
- **Audio devices on macOS / Windows** sometimes require a page reload after plugging in headset.
- **Cancelled calls leave orphan rows.** If user clicks Call then hangs up before Twilio's voice endpoint runs, a Call row exists with no `twilio_call_sid`. These rows can sit harmlessly in Phase 1.

## Cost expectations

At Phase 1 volume (10 calls/day, 5 min average, ~22 work days):
- Number rental: $1.15/month
- Outbound minutes: ~1,100 × $0.014 = $15.40
- Total: ~$17/month at moderate volume; ~$5/month at lower volume

No recording cost (per spec 11).
