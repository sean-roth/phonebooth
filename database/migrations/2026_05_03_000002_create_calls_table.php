<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('calls', function (Blueprint $table) {
            $table->id();

            $table->foreignId('lead_id')->constrained()->cascadeOnDelete();
            $table->string('twilio_call_sid', 50)->nullable();

            // Call metadata
            $table->unsignedInteger('duration_seconds')->nullable();
            $table->timestamp('started_at')->nullable();
            $table->timestamp('ended_at')->nullable();

            // Outcome — Sean's own observations
            $table->string('disposition', 30)->nullable();
            $table->text('pain_points')->nullable();
            $table->text('notes')->nullable();

            $table->timestamps();

            $table->index('twilio_call_sid');
            $table->index('disposition');
            $table->index('started_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('calls');
    }
};
