<?php

namespace App\Http\Controllers;

use App\Models\Call;
use App\Models\Lead;
use App\Services\EventLogger;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class CallController extends Controller
{
    public function create(Lead $lead)
    {
        $lead->load(['calls' => fn($q) => $q->orderByDesc('created_at')->limit(3)]);

        // If redirected back from a failed validation, the pending call still exists
        $pendingCall = $lead->calls()->whereNull('disposition')->latest()->first();

        return view('calls.create', compact('lead', 'pendingCall'));
    }

    public function store(Request $request, EventLogger $events)
    {
        $request->validate([
            'lead_id' => 'required|exists:leads,id',
        ]);

        $lead = Lead::findOrFail($request->input('lead_id'));

        $call = Call::create([
            'lead_id' => $lead->id,
            'started_at' => now(),
        ]);

        Log::channel('phonebooth_calls')->info('Call initiated', [
            'lead_id' => $lead->id,
            'call_id' => $call->id,
            'phone' => $lead->phone,
        ]);

        $events->record('call_initiated', 'call', $call->id, [
            'lead_id' => $lead->id,
            'phone' => $lead->phone,
        ]);

        return response()->json([
            'call_id' => $call->id,
            'to_number' => $lead->phone,
        ]);
    }

    public function update(Call $call, Request $request, EventLogger $events)
    {
        $validated = $request->validate([
            'disposition' => 'required|in:voicemail,no_answer,not_interested,interested,discovery_booked,disqualified,wrong_number,bad_number',
            'pain_points' => 'required_unless:disposition,voicemail,no_answer,wrong_number,bad_number',
            'notes' => 'nullable|string',
        ]);

        $call->update($validated + ['ended_at' => now()]);

        // Update lead: last_call_date always, status based on disposition
        $leadUpdate = ['last_call_date' => now()];

        $dispositionToStatus = [
            'not_interested' => 'not_interested',
            'interested' => 'interested',
            'discovery_booked' => 'discovery_booked',
            'disqualified' => 'disqualified',
            'wrong_number' => 'dead',
            'bad_number' => 'dead',
        ];

        if (isset($dispositionToStatus[$validated['disposition']])) {
            $leadUpdate['status'] = $dispositionToStatus[$validated['disposition']];
        } elseif (in_array($validated['disposition'], ['voicemail', 'no_answer'])) {
            // Keep current status — lead stays in queue for retry
            $leadUpdate['status'] = 'called';
        }

        $call->lead->update($leadUpdate);

        $events->record('call_completed', 'call', $call->id, [
            'disposition' => $call->disposition,
        ]);

        Log::channel('phonebooth_calls')->info('Call completed', [
            'call_id' => $call->id,
            'disposition' => $call->disposition,
        ]);

        if ($request->input('action') === 'next') {
            $nextLead = Lead::where('status', 'new')
                ->where('id', '!=', $call->lead_id)
                ->orderBy('id')
                ->first();

            return $nextLead
                ? redirect()->route('calls.create', $nextLead)
                : redirect()->route('leads.index')->with('info', 'No more new leads. Nice work.');
        }

        return redirect()->route('leads.show', $call->lead);
    }

    public function show(Call $call)
    {
        $call->load('lead');

        return view('calls.show', compact('call'));
    }
}
