<?php

namespace Database\Seeders;

use App\Models\Lead;
use Illuminate\Database\Seeder;

class LeadSeeder extends Seeder
{
    public function run(): void
    {
        $leads = [
            [
                'business_name' => 'Logan Square HVAC',
                'contact_name' => 'Bob Martinez',
                'phone' => '+17735550201',
                'email' => 'bob@lshvac.com',
                'website' => 'https://logansquarehvac.com',
                'industry' => 'HVAC',
                'neighborhood' => 'Logan Square',
                'address' => '2345 N Milwaukee Ave, Chicago, IL',
                'source' => 'seed',
            ],
            [
                'business_name' => 'Wicker Park Vintage',
                'contact_name' => 'Sarah Kim',
                'phone' => '+17735550202',
                'email' => 'sarah@wpvintage.com',
                'website' => 'https://wickerparkvintage.com',
                'industry' => 'Retail',
                'neighborhood' => 'Wicker Park',
                'address' => '1520 N Damen Ave, Chicago, IL',
                'source' => 'seed',
            ],
            [
                'business_name' => 'Pilsen Plumbing Co',
                'contact_name' => 'Carlos Rivera',
                'phone' => '+17735550203',
                'website' => 'https://pilsenplumbing.com',
                'industry' => 'Plumbing',
                'neighborhood' => 'Pilsen',
                'address' => '1801 W 18th St, Chicago, IL',
                'source' => 'seed',
            ],
            [
                'business_name' => 'Lincoln Park Dental',
                'contact_name' => 'Dr. Kim',
                'phone' => '+17735550204',
                'email' => 'kim@lpdental.com',
                'website' => 'https://lincolnparkdental.com',
                'industry' => 'Dental',
                'neighborhood' => 'Lincoln Park',
                'address' => '2400 N Clark St, Chicago, IL',
                'source' => 'seed',
            ],
            [
                'business_name' => 'Bridgeport Signs & Graphics',
                'contact_name' => 'Mike O\'Brien',
                'phone' => '+17735550205',
                'industry' => 'Signage',
                'neighborhood' => 'Bridgeport',
                'address' => '3100 S Halsted St, Chicago, IL',
                'source' => 'seed',
            ],
        ];

        foreach ($leads as $lead) {
            Lead::create($lead);
        }
    }
}
