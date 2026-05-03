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
