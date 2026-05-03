<?php

use App\Http\Controllers\CallController;
use App\Http\Controllers\LeadController;
use App\Http\Controllers\TwilioTokenController;
use App\Http\Controllers\TwilioWebhookController;
use Illuminate\Support\Facades\Route;

// Redirect root to leads
Route::get('/', fn() => redirect('/leads'));

// Leads
Route::get('/leads', [LeadController::class, 'index'])->name('leads.index');
Route::post('/leads/import', [LeadController::class, 'import'])->name('leads.import');
Route::get('/leads/{lead}', [LeadController::class, 'show'])->name('leads.show');
Route::patch('/leads/{lead}', [LeadController::class, 'update'])->name('leads.update');

// Calls
Route::get('/leads/{lead}/call', [CallController::class, 'create'])->name('calls.create');
Route::post('/calls', [CallController::class, 'store'])->name('calls.store');
Route::patch('/calls/{call}', [CallController::class, 'update'])->name('calls.update');
Route::get('/calls/{call}', [CallController::class, 'show'])->name('calls.show');

// Twilio webhooks (CSRF exempted in bootstrap/app.php)
Route::post('/webhooks/twilio/status', [TwilioWebhookController::class, 'status']);

// Twilio API (voice endpoint CSRF exempted in bootstrap/app.php)
Route::get('/api/twilio/token', [TwilioTokenController::class, 'generate']);
Route::post('/api/twilio/voice', [TwilioTokenController::class, 'voice']);
