<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ config('app.name') }} - @yield('title', 'Dashboard')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @stack('scripts')
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-white border-b border-gray-200 px-6 py-3">
        <div class="flex items-center justify-between max-w-7xl mx-auto">
            <a href="{{ route('leads.index') }}" class="text-lg font-bold text-gray-900">Phonebooth</a>
            <div class="text-sm text-gray-500">
                Phase 1 &mdash; {{ \App\Models\Lead::where('status', 'new')->count() }} leads queued
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-6 py-6">
        @if(session('success'))
            <div class="mb-4 rounded-md bg-green-50 border border-green-200 p-4 text-sm text-green-800">
                {{ session('success') }}
            </div>
        @endif

        @if(session('error'))
            <div class="mb-4 rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">
                {{ session('error') }}
            </div>
        @endif

        @if(session('info'))
            <div class="mb-4 rounded-md bg-blue-50 border border-blue-200 p-4 text-sm text-blue-800">
                {{ session('info') }}
            </div>
        @endif

        @yield('content')
    </main>
</body>
</html>
