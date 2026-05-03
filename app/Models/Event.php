<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    public $timestamps = false;

    protected $fillable = ['event_type', 'subject_type', 'subject_id', 'payload', 'created_at'];

    protected $casts = [
        'payload' => 'array',
        'created_at' => 'datetime',
    ];
}
