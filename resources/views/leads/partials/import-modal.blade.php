<dialog id="import-modal" class="rounded-lg p-6 shadow-xl backdrop:bg-gray-900/50 max-w-md w-full">
    <h2 class="text-lg font-bold text-gray-900 mb-4">Import Leads from CSV</h2>

    <p class="text-sm text-gray-600 mb-4">
        CSV must have <strong>business_name</strong> and <strong>phone</strong> columns.
        Optional: contact_name, email, website, industry, neighborhood, address.
    </p>

    <form action="{{ route('leads.import') }}" method="POST" enctype="multipart/form-data">
        @csrf
        <div class="mb-4">
            <input type="file" name="csv_file" accept=".csv,.txt" required
                   class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200">
        </div>

        <div class="flex gap-3 justify-end">
            <button type="button" onclick="document.getElementById('import-modal').close()"
                    class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
                Cancel
            </button>
            <button type="submit" class="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                Import
            </button>
        </div>
    </form>
</dialog>
