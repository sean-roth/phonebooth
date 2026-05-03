@extends('layouts.app')

@section('title', 'Call ' . $lead->business_name)

@push('scripts')
    @vite('resources/js/cockpit.js')
@endpush

@section('content')
<div class="mb-4">
    <a href="{{ route('leads.show', $lead) }}" class="text-sm text-gray-500 hover:text-gray-700">&larr; {{ $lead->business_name }}</a>
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {{-- Left: Lead info + brief --}}
    <div>
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-1">{{ $lead->business_name }}</h1>
            @if($lead->contact_name)
                <p class="text-lg text-gray-600 mb-2">{{ $lead->contact_name }}</p>
            @endif

            <div class="text-sm text-gray-500 space-y-1 mb-4">
                <div>{{ $lead->phone }}</div>
                @if($lead->website)
                    <div><a href="{{ $lead->website }}" target="_blank" class="text-blue-600 hover:underline">{{ $lead->website }}</a></div>
                @endif
                @if($lead->neighborhood || $lead->industry)
                    <div>{{ collect([$lead->neighborhood, $lead->industry])->filter()->join(' · ') }}</div>
                @endif
            </div>

            @if($lead->brief)
                <div class="border-t border-gray-200 pt-4 mt-4">
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">Brief</h3>
                    <div class="prose prose-sm max-w-none text-gray-700">
                        {!! Str::markdown($lead->brief) !!}
                    </div>
                </div>
            @else
                <div class="border-t border-gray-200 pt-4 mt-4 text-sm text-gray-400">
                    No brief written. <a href="{{ route('leads.show', $lead) }}" class="text-blue-600 hover:underline">Add one</a>.
                </div>
            @endif

            {{-- Recent calls for context --}}
            @if($lead->calls->isNotEmpty())
                <div class="border-t border-gray-200 pt-4 mt-4">
                    <h3 class="text-sm font-semibold text-gray-700 mb-2">Recent Calls</h3>
                    @foreach($lead->calls as $prevCall)
                        <div class="text-sm text-gray-500 mb-1">
                            {{ $prevCall->created_at->format('M j') }} &mdash;
                            {{ ucfirst(str_replace('_', ' ', $prevCall->disposition ?? 'in progress')) }}
                            @if($prevCall->pain_points)
                                <span class="text-gray-400">| {{ Str::limit($prevCall->pain_points, 60) }}</span>
                            @endif
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>

    {{-- Right: Dialer + post-call form --}}
    <div>
        {{-- Dialer --}}
        <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <span id="call-status" class="text-sm font-medium text-gray-400">Initializing...</span>
                <span id="call-timer" class="text-2xl font-mono text-gray-900">00:00</span>
            </div>

            <div class="flex gap-3">
                <button id="call-btn"
                        data-phone="{{ $lead->phone }}"
                        data-lead-id="{{ $lead->id }}"
                        class="flex-1 bg-green-600 text-white px-6 py-3 rounded-md text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
                    Call {{ $lead->contact_name ?? $lead->business_name }}
                </button>
                <button id="hangup-btn"
                        class="hidden flex-1 bg-red-600 text-white px-6 py-3 rounded-md text-sm font-medium hover:bg-red-700">
                    Hang Up
                </button>
            </div>
        </div>

        {{-- Post-call form --}}
        @php
            // If we have a pending call (validation failure redirect), pre-enable the form
            $formEnabled = isset($pendingCall) && $pendingCall && $errors->any();
            $formAction = $formEnabled ? route('calls.update', $pendingCall) : '';
        @endphp
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-sm font-semibold text-gray-900 mb-4">Post-Call Notes</h2>

            @if($errors->any())
                <div class="mb-4 rounded-md bg-red-50 border border-red-200 p-3">
                    <ul class="text-sm text-red-800 list-disc list-inside">
                        @foreach($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </div>
            @endif

            <form id="post-call-form" method="POST" action="{{ $formAction }}" class="{{ $formEnabled ? '' : 'opacity-50' }}">
                @csrf
                @method('PATCH')
                <input type="hidden" id="action-input" name="action" value="stay">

                <div class="mb-4">
                    <label for="disposition" class="block text-sm font-medium text-gray-700 mb-1">Disposition *</label>
                    <select name="disposition" id="disposition" {{ $formEnabled ? '' : 'disabled' }} class="w-full rounded-md border-gray-300 text-sm">
                        <option value="">Select...</option>
                        @foreach([
                            'voicemail' => 'Voicemail left',
                            'no_answer' => 'No answer / disconnected',
                            'not_interested' => 'Not interested',
                            'interested' => 'Interested — follow up',
                            'discovery_booked' => 'Discovery call booked',
                            'disqualified' => 'Disqualified',
                            'wrong_number' => 'Wrong number',
                            'bad_number' => 'Bad number / dead line',
                        ] as $value => $label)
                            <option value="{{ $value }}" {{ old('disposition') === $value ? 'selected' : '' }}>{{ $label }}</option>
                        @endforeach
                    </select>
                    @error('disposition')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div class="mb-4">
                    <label for="pain_points" class="block text-sm font-medium text-gray-700 mb-1">
                        Pain Points <span class="text-gray-400 font-normal">(required unless voicemail/no answer/wrong/bad number)</span>
                    </label>
                    <textarea name="pain_points" id="pain_points" rows="3" {{ $formEnabled ? '' : 'disabled' }}
                              class="w-full rounded-md border-gray-300 text-sm"
                              placeholder="What did the lead complain about? What eats their time?">{{ old('pain_points') }}</textarea>
                    @error('pain_points')
                        <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                    @enderror
                </div>

                <div class="mb-4">
                    <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
                        Notes <span class="text-gray-400 font-normal">(optional)</span>
                    </label>
                    <textarea name="notes" id="notes" rows="3" {{ $formEnabled ? '' : 'disabled' }}
                              class="w-full rounded-md border-gray-300 text-sm"
                              placeholder="Your reflection: opened too fast, good rapport, should have asked X...">{{ old('notes') }}</textarea>
                </div>

                <div class="flex gap-3">
                    <button type="submit" data-action="next" {{ $formEnabled ? '' : 'disabled' }}
                            class="flex-1 bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 disabled:opacity-50">
                        Save and Next
                    </button>
                    <button type="submit" data-action="stay" {{ $formEnabled ? '' : 'disabled' }}
                            class="flex-1 bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 disabled:opacity-50">
                        Save and Stay
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
@endsection
