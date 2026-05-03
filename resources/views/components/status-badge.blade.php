@props(['status'])

@php
$colors = [
    'new' => 'bg-blue-100 text-blue-800',
    'called' => 'bg-yellow-100 text-yellow-800',
    'interested' => 'bg-green-100 text-green-800',
    'discovery_booked' => 'bg-purple-100 text-purple-800',
    'discovery_completed' => 'bg-indigo-100 text-indigo-800',
    'disqualified' => 'bg-red-100 text-red-800',
    'not_interested' => 'bg-gray-100 text-gray-600',
    'dead' => 'bg-gray-200 text-gray-500',
];
$class = $colors[$status] ?? 'bg-gray-100 text-gray-600';
$label = str_replace('_', ' ', $status);
@endphp

<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold {{ $class }}">
    {{ ucfirst($label) }}
</span>
