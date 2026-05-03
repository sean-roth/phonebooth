<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Twilio\Security\RequestValidator;

class VerifyTwilioSignature
{
    public function handle(Request $request, Closure $next)
    {
        $authToken = config('services.twilio.auth_token');

        if (!$authToken) {
            abort(503, 'Twilio auth token not configured');
        }

        $validator = new RequestValidator($authToken);

        $signature = $request->header('X-Twilio-Signature', '');
        $url = config('app.tunnel_url') . $request->getPathInfo();
        $params = $request->all();

        if (!$validator->validate($signature, $url, $params)) {
            abort(403, 'Invalid Twilio signature');
        }

        return $next($request);
    }
}
