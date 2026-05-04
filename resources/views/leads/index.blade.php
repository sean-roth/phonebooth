@extends('layouts.app')

@section('title', 'Leads')

@section('content')
<div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold text-gray-900">Leads</h1>
    <div class="flex gap-2">
        <button onclick="document.getElementById('add-lead-modal').showModal()" class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
            Add Lead
        </button>
        <button onclick="document.getElementById('import-modal').showModal()" class="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
            Import CSV
        </button>
    </div>
</div>

{{-- Status filter --}}
<div class="flex gap-2 mb-4 flex-wrap">
    <a href="{{ route('leads.index') }}"
       class="px-3 py-1 rounded-full text-sm font-medium {{ !request('status') ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200' }}">
        All ({{ \App\Models\Lead::count() }})
    </a>
    @foreach(['new', 'called', 'interested', 'discovery_booked', 'discovery_completed', 'not_interested', 'disqualified', 'dead'] as $s)
        @php $count = \App\Models\Lead::where('status', $s)->count(); @endphp
        @if($count > 0)
        <a href="{{ route('leads.index', ['status' => $s]) }}"
           class="px-3 py-1 rounded-full text-sm font-medium {{ request('status') === $s ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200' }}">
            {{ ucfirst(str_replace('_', ' ', $s)) }} ({{ $count }})
        </a>
        @endif
    @endforeach
</div>

{{-- Leads table --}}
@if($leads->isEmpty())
    <div class="text-center py-12 text-gray-500">
        <p class="text-lg mb-2">No leads yet.</p>
        <p class="text-sm">Import a CSV to get started.</p>
    </div>
@else
    <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Business</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Neighborhood</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Industry</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Call</th>
                    <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase"></th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
                @foreach($leads as $lead)
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-3">
                        <a href="{{ route('leads.show', $lead) }}" class="text-sm font-medium text-gray-900 hover:underline">
                            {{ $lead->business_name }}
                        </a>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ $lead->contact_name ?? '—' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ $lead->neighborhood ?? '—' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ $lead->industry ?? '—' }}</td>
                    <td class="px-4 py-3"><x-status-badge :status="$lead->status" /></td>
                    <td class="px-4 py-3 text-sm text-gray-500">
                        {{ $lead->last_call_date?->format('M j, g:ia') ?? '—' }}
                    </td>
                    <td class="px-4 py-3 text-right">
                        <div class="flex items-center justify-end gap-3">
                            <a href="{{ route('calls.create', $lead) }}" class="text-sm font-medium text-blue-600 hover:text-blue-800">
                                Call
                            </a>
                            <form action="{{ route('leads.destroy', $lead) }}" method="POST" class="inline"
                                  onsubmit="return confirm('Delete {{ addslashes($lead->business_name) }}?@if($lead->calls_count > 0) This will also delete {{ $lead->calls_count }} call record{{ $lead->calls_count === 1 ? '' : 's' }}.@endif');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="text-gray-400 hover:text-red-600" title="Delete lead">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22M9 7V4a1 1 0 011-1h4a1 1 0 011 1v3" />
                                    </svg>
                                </button>
                            </form>
                        </div>
                    </td>
                </tr>
                @endforeach
            </tbody>
        </table>
    </div>
@endif

@include('leads.partials.import-modal')
@include('leads.partials.add-lead-modal')
@endsection
