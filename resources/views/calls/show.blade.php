@extends('layouts.app')

@section('title', 'Call with ' . $call->lead->business_name)

@section('content')
<div class="mb-4">
    <a href="{{ route('leads.show', $call->lead) }}" class="text-sm text-gray-500 hover:text-gray-700">&larr; {{ $call->lead->business_name }}</a>
</div>

<div class="bg-white rounded-lg border border-gray-200 p-6 max-w-2xl">
    <h1 class="text-xl font-bold text-gray-900 mb-1">Call with {{ $call->lead->business_name }}</h1>
    <p class="text-sm text-gray-500 mb-4">
        {{ $call->started_at?->format('M j, Y g:ia') ?? $call->created_at->format('M j, Y g:ia') }}
        @if($call->duration_seconds)
            &mdash; {{ gmdate('i:s', $call->duration_seconds) }}
        @endif
    </p>

    @if($call->disposition)
        <div class="mb-4">
            <h2 class="text-sm font-semibold text-gray-700 mb-1">Disposition</h2>
            <p class="text-gray-900">{{ ucfirst(str_replace('_', ' ', $call->disposition)) }}</p>
        </div>
    @endif

    @if($call->pain_points)
        <div class="mb-4">
            <h2 class="text-sm font-semibold text-gray-700 mb-1">Pain Points</h2>
            <div class="prose prose-sm max-w-none text-gray-700">
                {!! Str::markdown($call->pain_points) !!}
            </div>
        </div>
    @endif

    @if($call->notes)
        <div class="mb-4">
            <h2 class="text-sm font-semibold text-gray-700 mb-1">Notes</h2>
            <div class="prose prose-sm max-w-none text-gray-700">
                {!! Str::markdown($call->notes) !!}
            </div>
        </div>
    @endif
</div>
@endsection
