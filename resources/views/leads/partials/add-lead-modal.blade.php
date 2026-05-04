<dialog id="add-lead-modal" class="rounded-lg p-6 shadow-xl backdrop:bg-gray-900/50 max-w-2xl w-full">
    <h2 class="text-lg font-bold text-gray-900 mb-4">Add Lead</h2>

    <form action="{{ route('leads.store') }}" method="POST">
        @csrf

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
                <label for="al-business_name" class="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
                <input type="text" name="business_name" id="al-business_name" required
                       value="{{ old('business_name') }}"
                       class="w-full rounded-md border-gray-300 text-sm">
                @error('business_name')<p class="mt-1 text-sm text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <label for="al-contact_name" class="block text-sm font-medium text-gray-700 mb-1">Contact Name</label>
                <input type="text" name="contact_name" id="al-contact_name"
                       value="{{ old('contact_name') }}"
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div>
                <label for="al-phone" class="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                <input type="text" name="phone" id="al-phone" required
                       value="{{ old('phone') }}"
                       placeholder="312-555-1234 or +13125551234"
                       class="w-full rounded-md border-gray-300 text-sm">
                @error('phone')<p class="mt-1 text-sm text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <label for="al-email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" name="email" id="al-email"
                       value="{{ old('email') }}"
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div>
                <label for="al-website" class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                <input type="text" name="website" id="al-website"
                       value="{{ old('website') }}"
                       placeholder="https://"
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div>
                <label for="al-industry" class="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                <input type="text" name="industry" id="al-industry"
                       value="{{ old('industry') }}"
                       placeholder="HVAC, Retail, Plumbing..."
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div>
                <label for="al-neighborhood" class="block text-sm font-medium text-gray-700 mb-1">Neighborhood</label>
                <input type="text" name="neighborhood" id="al-neighborhood"
                       value="{{ old('neighborhood') }}"
                       placeholder="Logan Square, Wicker Park..."
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div class="md:col-span-2">
                <label for="al-address" class="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input type="text" name="address" id="al-address"
                       value="{{ old('address') }}"
                       class="w-full rounded-md border-gray-300 text-sm">
            </div>

            <div class="md:col-span-2">
                <label for="al-brief" class="block text-sm font-medium text-gray-700 mb-1">Brief (markdown, optional)</label>
                <textarea name="brief" id="al-brief" rows="4"
                          placeholder="Pre-call research, talking points, observations from their website..."
                          class="w-full rounded-md border-gray-300 text-sm font-mono">{{ old('brief') }}</textarea>
            </div>
        </div>

        <div class="flex gap-3 justify-end">
            <button type="button" onclick="document.getElementById('add-lead-modal').close()"
                    class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
                Cancel
            </button>
            <button type="submit" class="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Add Lead
            </button>
        </div>
    </form>
</dialog>

@if($errors->any() && old('business_name'))
    <script>document.getElementById('add-lead-modal').showModal();</script>
@endif
