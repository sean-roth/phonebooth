<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('leads', function (Blueprint $table) {
            $table->id();

            // Identity
            $table->string('business_name');
            $table->string('contact_name')->nullable();
            $table->string('phone', 20)->unique();
            $table->string('email')->nullable();
            $table->string('website')->nullable();

            // Categorization
            $table->string('industry', 100)->nullable();
            $table->string('neighborhood', 100)->nullable();
            $table->string('address')->nullable();

            // Brief and notes
            $table->text('brief')->nullable();
            $table->string('source', 50)->nullable();

            // Status tracking
            $table->string('status', 30)->default('new');
            $table->timestamp('last_call_date')->nullable();

            $table->timestamps();

            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('leads');
    }
};
