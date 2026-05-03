<?php

namespace App\Http\Controllers;

use App\Models\Lead;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class LeadController extends Controller
{
    public function index(Request $request)
    {
        $query = Lead::query();

        if ($status = $request->query('status')) {
            $query->where('status', $status);
        }

        $leads = $query->orderByRaw("CASE status
            WHEN 'new' THEN 1
            WHEN 'interested' THEN 2
            WHEN 'discovery_booked' THEN 3
            WHEN 'called' THEN 4
            WHEN 'discovery_completed' THEN 5
            WHEN 'not_interested' THEN 6
            WHEN 'disqualified' THEN 7
            WHEN 'dead' THEN 8
            ELSE 9 END")
            ->orderBy('id')
            ->get();

        return view('leads.index', compact('leads'));
    }

    public function import(Request $request)
    {
        $request->validate([
            'csv_file' => 'required|file|mimes:csv,txt',
        ]);

        $file = $request->file('csv_file');
        $handle = fopen($file->getPathname(), 'r');

        if (!$handle) {
            return back()->with('error', 'Could not open CSV file.');
        }

        $headers = fgetcsv($handle);
        if (!$headers) {
            fclose($handle);
            return back()->with('error', 'CSV file is empty or has no headers.');
        }

        $headers = array_map(fn($h) => strtolower(trim($h)), $headers);

        $validColumns = ['business_name', 'contact_name', 'phone', 'email', 'website', 'industry', 'neighborhood', 'address'];
        $columnMap = [];
        foreach ($headers as $index => $header) {
            if (in_array($header, $validColumns)) {
                $columnMap[$header] = $index;
            }
        }

        if (!isset($columnMap['business_name']) || !isset($columnMap['phone'])) {
            fclose($handle);
            return back()->with('error', 'CSV must have business_name and phone columns.');
        }

        $imported = 0;
        $skipped = 0;
        $rejected = 0;

        DB::beginTransaction();

        try {
            while (($row = fgetcsv($handle)) !== false) {
                $data = [];
                foreach ($columnMap as $column => $index) {
                    $data[$column] = trim($row[$index] ?? '');
                }

                if (empty($data['business_name']) || empty($data['phone'])) {
                    $rejected++;
                    continue;
                }

                $phone = $this->normalizePhone($data['phone']);
                if (!$phone) {
                    $rejected++;
                    continue;
                }

                if (Lead::where('phone', $phone)->exists()) {
                    $skipped++;
                    continue;
                }

                $data['phone'] = $phone;
                $data['source'] = 'csv_import';
                Lead::create($data);
                $imported++;
            }

            DB::commit();
        } catch (\Exception $e) {
            DB::rollBack();
            fclose($handle);
            return back()->with('error', 'Import failed: ' . $e->getMessage());
        }

        fclose($handle);

        return redirect()->route('leads.index')
            ->with('success', "Imported {$imported}, skipped {$skipped} duplicates, rejected {$rejected} invalid.");
    }

    public function show(Lead $lead)
    {
        $lead->load(['calls' => fn($q) => $q->orderByDesc('created_at')]);

        return view('leads.show', compact('lead'));
    }

    public function update(Lead $lead, Request $request)
    {
        $validated = $request->validate([
            'brief' => 'nullable|string',
            'status' => 'nullable|in:new,called,interested,discovery_booked,discovery_completed,disqualified,not_interested,dead',
        ]);

        $lead->update(array_filter($validated, fn($v) => $v !== null));

        return back()->with('success', 'Lead updated.');
    }

    private function normalizePhone(string $phone): ?string
    {
        $digits = preg_replace('/\D/', '', $phone);

        if (strlen($digits) === 10) {
            return '+1' . $digits;
        }

        if (strlen($digits) === 11 && str_starts_with($digits, '1')) {
            return '+' . $digits;
        }

        return null;
    }
}
