<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Lead extends Model
{
    protected $fillable = [
        'business_name', 'contact_name', 'phone', 'email', 'website',
        'industry', 'neighborhood', 'address', 'brief', 'source', 'status',
        'last_call_date',
    ];

    protected $casts = [
        'last_call_date' => 'datetime',
    ];

    public function calls(): HasMany
    {
        return $this->hasMany(Call::class);
    }
}
