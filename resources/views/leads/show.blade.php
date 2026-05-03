@extends('layouts.app')

@section('title', $lead->business_name)

@section('content')
<div class="mb-4">
    <a href="{{ route('leads.index') }}" class="text-sm text-gray-500 hover:text-gray-700">&larr; All Leads</a>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    {{-- Lead info + edit --}}
    <div class="lg:col-span-2">
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">{{ $lead->business_name }}</h1>
                    @if($lead->contact_name)
                        <p class="text-gray-600 mt-1">{{ $lead->contact_name }}</p>
                    @endif
                </div>
                <x-status-badge :status="$lead->status" />
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm mb-6">
                <div>
                    <span class="text-gray-500">Phone:</span>
                    <span class="text-gray-900 font-medium ml-1">{{ $lead->phone }}</span>
                </div>
                @if($lead->email)
                <div>
                    <span class="text-gray-500">Email:</span>
                    <span class="text-gray-900 ml-1">{{ $lead->email }}</span>
                </div>
                @endif
                @if($lead->website)
                <div>
                    <span class="text-gray-500">Website:</span>
                    <a href="{{ $lead->website }}" target="_blank" class="text-blue-600 hover:underline ml-1">{{ $lead->website }}</a>
                </div>
                @endif
                @if($lead->industry)
                <div>
                    <span class="text-gray-500">Industry:</span>
                    <span class="text-gray-900 ml-1">{{ $lead->industry }}</span>
                </div>
                @endif
                @if($lead->neighborhood)
                <div>
                    <span class="text-gray-500">Neighborhood:</span>
                    <span class="text-gray-900 ml-1">{{ $lead->neighborhood }}</span>
                </div>
                @endif
                @if($lead->address)
                <div class="col-span-2">
                    <span class="text-gray-500">Address:</span>
                    <span class="text-gray-900 ml-1">{{ $lead->address }}</span>
                </div>
                @endif
            </div>

            <form action="{{ route('leads.update', $lead) }}" method="POST">
                @csrf
                @method('PATCH')

                <div class="mb-4">
                    <label for="status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select name="status" id="status" class="w-full rounded-md border-gray-300 text-sm">
                        @foreach(['new', 'called', 'interested', 'discovery_booked', 'discovery_completed', 'not_interested', 'disqualified', 'dead'] as $s)
                            <option value="{{ $s }}" {{ $lead->status === $s ? 'selected' : '' }}>
                                {{ ucfirst(str_replace('_', ' ', $s)) }}
                            </option>
                        @endforeach
                    </select>
                </div>

                <div class="mb-4">
                    <label for="brief" class="block text-sm font-medium text-gray-700 mb-1">Brief (markdown)</label>
                    <textarea name="brief" id="brief" rows="8" class="w-full rounded-md border-gray-300 text-sm font-mono"
                              placeholder="Pre-call research notes, talking points, observations...">{{ old('brief', $lead->brief) }}</textarea>
                </div>

                <button type="submit" class="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                    Save
                </button>
            </form>
        </div>
    </div>

    {{-- Sidebar: call history + actions --}}
    <div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 mb-4">
            <a href="{{ route('calls.create', $lead) }}" class="block w-full bg-blue-600 text-white text-center px-4 py-3 rounded-md text-sm font-medium hover:bg-blue-700">
                Call This Lead
            </a>
        </div>

        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-sm font-semibold text-gray-900 mb-3">Call History</h2>

            @if($lead->calls->isEmpty())
                <p class="text-sm text-gray-500">No calls yet.</p>
            @else
                <div class="space-y-3">
                    @foreach($lead->calls as $call)
                    <a href="{{ route('calls.show', $call) }}" class="block p-3 rounded-md border border-gray-100 hover:bg-gray-50">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-sm text-gray-900">{{ $call->created_at->format('M j, g:ia') }}</span>
                            @if($call->duration_seconds)
                                <span class="text-xs text-gray-500">{{ gmdate('i:s', $call->duration_seconds) }}</span>
                            @endif
                        </div>
                        @if($call->disposition)
                            <span class="text-xs text-gray-600">{{ ucfirst(str_replace('_', ' ', $call->disposition)) }}</span>
                        @endif
                    </a>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
@endsection
