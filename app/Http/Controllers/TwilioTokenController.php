<?php

namespace App\Http\Controllers;

use App\Models\Call;
use App\Services\EventLogger;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
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

        if (!$accountSid || !$apiKeySid || !$apiKeySecret || !$twimlAppSid) {
            return response()->json([
                'error' => 'Twilio not configured. Fill in TWILIO_* env vars.',
            ], 503);
        }

        $identity = 'phonebooth-user';

        $token = new AccessToken(
            $accountSid,
            $apiKeySid,
            $apiKeySecret,
            3600,
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

    public function voice(Request $request, EventLogger $events)
    {
        $toNumber = $request->input('To');
        $callId = $request->input('call_id');
        $twilioCallSid = $request->input('CallSid');
        $fromNumber = config('services.twilio.phone_number');

        Log::channel('phonebooth_calls')->info('Voice endpoint hit', [
            'to' => $toNumber,
            'call_id' => $callId,
            'twilio_call_sid' => $twilioCallSid,
        ]);

        if ($callId && $twilioCallSid) {
            Call::where('id', $callId)->update([
                'twilio_call_sid' => $twilioCallSid,
            ]);

            $events->record('twilio_call_connected', 'call', (int) $callId, [
                'twilio_call_sid' => $twilioCallSid,
            ]);
        }

        $twiml = new \Twilio\TwiML\VoiceResponse();
        $dial = $twiml->dial('', [
            'callerId' => $fromNumber,
        ]);
        $dial->number($toNumber);

        return response($twiml, 200)->header('Content-Type', 'text/xml');
    }
}
