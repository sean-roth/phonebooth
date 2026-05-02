# 05 — Whisper + Claude Integration

## Purpose of this document

The post-call processing pipeline. Triggered when the user clicks "Process Call" on the call detail page. Downloads audio, transcribes locally with faster-whisper, sends transcript to Claude API for coaching feedback, saves both to the call row.

## What needs to exist before coding

1. Python 3.10+ on the OptiPlex (already present per Sean's setup)
2. ffmpeg installed (`apt install ffmpeg` on Ubuntu — required for audio decoding)
3. faster-whisper Python package: `pip install faster-whisper`
4. The `small` model will auto-download on first use (~460MB) to `~/.cache/huggingface/`
5. Anthropic API key in `.env` as `ANTHROPIC_API_KEY`

Note on the Claude API: there is no official Anthropic PHP SDK at time of writing. The integration uses Laravel's built-in HTTP client (`Illuminate\Support\Facades\Http`) to call the Messages API directly. No additional Composer package is needed for the Claude integration.

## Pipeline overview

```
User clicks "Process Call"
  │
  ▼
1. Download recording from Twilio URL → storage/recordings/{call_id}.mp3
  │
  ▼
2. Run faster-whisper subprocess on mp3 → transcript text
  │
  ▼
3. Save transcript to call row
  │
  ▼
4. Build coaching prompt (skill template + transcript + metadata)
  │
  ▼
5. Call Claude API → coaching markdown
  │
  ▼
6. Save coaching feedback to call row
  │
  ▼
7. Set processed_at = now()
  │
  ▼
Redirect user to call detail page
```

For Phase 1, this entire pipeline runs synchronously in the request. A 5-minute call processes in ~60-90 seconds total. Show a loading spinner. Phase 2 should move this to a queued job.

**Browser timeout warning:** Some browsers and proxies time out fetch/XHR requests at 60 seconds. The Process Call action can exceed this. Two options for Phase 1:

- Use a regular form POST (not fetch) — browsers wait indefinitely on form submissions, with a visible loading indicator
- Or set up the action as a redirect-after-POST pattern with a status-polling page

The form POST approach is simpler and matches Laravel's default flow. Recommend that.

## Component 1: Recording download

`app/Services/RecordingDownloader.php`:

```php
<?php

namespace App\Services;

use App\Models\Call;
use Illuminate\Support\Facades\Http;

class RecordingDownloader
{
    public function download(Call $call): string
    {
        if ($call->recording_local_path && file_exists($call->recording_local_path)) {
            return $call->recording_local_path;
        }

        if (!$call->recording_url) {
            throw new \Exception('No recording URL on call.');
        }

        $accountSid = config('services.twilio.account_sid');
        $authToken = config('services.twilio.auth_token');

        // Twilio recording URLs require basic auth
        $response = Http::withBasicAuth($accountSid, $authToken)
            ->timeout(60)
            ->get($call->recording_url);

        if (!$response->successful()) {
            throw new \Exception('Failed to download recording: ' . $response->status());
        }

        $directory = storage_path('app/recordings');
        if (!is_dir($directory)) {
            mkdir($directory, 0755, true);
        }

        $path = $directory . '/' . $call->id . '.mp3';
        file_put_contents($path, $response->body());

        $call->update(['recording_local_path' => $path]);

        return $path;
    }
}
```

## Component 2: Whisper transcription

The cleanest approach is a small Python script that takes a path argument and prints the transcript to stdout. Laravel calls it as a subprocess.

`scripts/transcribe.py`:

```python
#!/usr/bin/env python3
"""Transcribe an audio file using faster-whisper. Prints transcript to stdout."""

import sys
import os
from faster_whisper import WhisperModel


def format_timestamp(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def main():
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file_path>", file=sys.stderr)
        sys.exit(1)

    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    model_size = os.environ.get("WHISPER_MODEL", "small")
    device = os.environ.get("WHISPER_DEVICE", "cpu")
    compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

    # Initialize model. First run downloads from HuggingFace (~460MB for small).
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # Transcribe. The recording is dual-channel (left=user, right=lead);
    # faster-whisper handles this by default by mixing channels.
    segments, info = model.transcribe(
        audio_path,
        language="en",
        beam_size=5,
        vad_filter=True,  # voice activity detection — skip silence
    )

    # Output: timestamped lines, one per segment
    for segment in segments:
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        print(f"[{start} - {end}] {segment.text.strip()}")


if __name__ == "__main__":
    main()
```

Make it executable: `chmod +x scripts/transcribe.py`

`app/Services/Transcriber.php`:

```php
<?php

namespace App\Services;

use App\Models\Call;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class Transcriber
{
    public function transcribe(Call $call): string
    {
        if (!$call->recording_local_path) {
            throw new \Exception('Recording not downloaded yet.');
        }

        $script = base_path('scripts/transcribe.py');
        $python = config('services.whisper.python_path', 'python3');

        $process = new Process([
            $python,
            $script,
            $call->recording_local_path,
        ]);

        $process->setEnv([
            'WHISPER_MODEL' => config('services.whisper.model', 'small'),
            'WHISPER_DEVICE' => config('services.whisper.device', 'cpu'),
            'WHISPER_COMPUTE_TYPE' => config('services.whisper.compute_type', 'int8'),
        ]);

        $process->setTimeout(300);  // 5 minutes max for transcription
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        $transcript = $process->getOutput();

        if (empty(trim($transcript))) {
            throw new \Exception('Whisper returned empty transcript.');
        }

        $call->update(['transcript' => $transcript]);

        return $transcript;
    }
}
```

`config/services.php` additions:

```php
'whisper' => [
    'python_path' => env('WHISPER_PYTHON_PATH', 'python3'),
    'model' => env('WHISPER_MODEL', 'small'),
    'device' => env('WHISPER_DEVICE', 'cpu'),
    'compute_type' => env('WHISPER_COMPUTE_TYPE', 'int8'),
],

'anthropic' => [
    'api_key' => env('ANTHROPIC_API_KEY'),
    'model' => env('CLAUDE_MODEL', 'claude-sonnet-4-6'),
],
```

## Component 3: Coaching feedback via Claude

`app/Services/CoachingGenerator.php`:

```php
<?php

namespace App\Services;

use App\Models\Call;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\File;

class CoachingGenerator
{
    public function generate(Call $call, string $framework = 'jeb_blount'): string
    {
        if (!$call->transcript) {
            throw new \Exception('Call has no transcript yet.');
        }

        $skillContent = $this->loadSkill($framework);
        $prompt = $this->buildPrompt($skillContent, $call);

        $response = Http::withHeaders([
            'x-api-key' => config('services.anthropic.api_key'),
            'anthropic-version' => '2023-06-01',
            'content-type' => 'application/json',
        ])
        ->timeout(120)
        ->retry(2, 1000)
        ->post('https://api.anthropic.com/v1/messages', [
            'model' => config('services.anthropic.model'),
            'max_tokens' => 4096,
            'messages' => [
                ['role' => 'user', 'content' => $prompt],
            ],
        ]);

        if (!$response->successful()) {
            throw new \Exception('Claude API error: ' . $response->body());
        }

        $data = $response->json();
        $feedback = $data['content'][0]['text'] ?? '';

        if (empty($feedback)) {
            throw new \Exception('Claude returned empty response.');
        }

        $call->update([
            'coaching_feedback' => $feedback,
            'coaching_framework' => $framework,
        ]);

        return $feedback;
    }

    private function loadSkill(string $framework): string
    {
        $skillMap = [
            'jeb_blount' => 'docs/skills/01-jeb-blount.md',
            'spin' => 'docs/skills/02-spin.md',
        ];

        if (!isset($skillMap[$framework])) {
            throw new \Exception("Unknown framework: {$framework}");
        }

        return File::get(base_path($skillMap[$framework]));
    }

    private function buildPrompt(string $skillContent, Call $call): string
    {
        $lead = $call->lead;
        $disposition = $call->disposition ?? 'unknown';
        $painPoints = $call->pain_points ?? '(none captured)';
        $notes = $call->notes ?? '(none)';
        $duration = $call->duration_seconds ?? 0;

        return <<<PROMPT
{$skillContent}

---

# Call to evaluate

**Lead:** {$lead->business_name}
**Industry:** {$lead->industry}
**Contact:** {$lead->contact_name}
**Disposition:** {$disposition}
**Duration:** {$duration} seconds

**Pain points captured:**
{$painPoints}

**User's own notes:**
{$notes}

**Transcript:**
{$call->transcript}

---

Now evaluate this call against the framework above. Follow the framework's rubric and output structure exactly.
PROMPT;
    }
}
```

## Component 4: The orchestrator

`app/Http/Controllers/CallController.php` — `process()` method:

```php
public function process(Call $call, RecordingDownloader $downloader, Transcriber $transcriber, CoachingGenerator $coach)
{
    try {
        if (!$call->recording_local_path) {
            $downloader->download($call);
            $call->refresh();
        }

        if (!$call->transcript) {
            $transcriber->transcribe($call);
            $call->refresh();
        }

        $framework = config('services.coaching.default_framework', 'jeb_blount');
        $coach->generate($call, $framework);

        $call->update(['processed_at' => now()]);

        return redirect()->route('calls.show', $call)
            ->with('success', 'Call processed successfully.');

    } catch (\Exception $e) {
        \Log::error('Process call failed', ['call_id' => $call->id, 'error' => $e->getMessage()]);
        return redirect()->route('calls.show', $call)
            ->with('error', 'Processing failed: ' . $e->getMessage());
    }
}
```

`config/services.php`:
```php
'coaching' => [
    'default_framework' => env('COACHING_DEFAULT_FRAMEWORK', 'jeb_blount'),
],
```

## What the user sees

When user clicks "Process Call":
1. Page submits POST to `/calls/{id}/process` (use a form POST, not fetch — browsers wait without timeout)
2. Server takes 60-90 seconds (download ~5s, transcribe ~30s, claude ~10-30s)
3. Browser shows loading state (spinner + "Transcribing... this takes about a minute" message)
4. Server redirects to `/calls/{id}` with success or error flash
5. User sees full transcript and coaching feedback

For Phase 1's synchronous approach, the spinner should be honest:
```html
<form method="POST" action="/calls/{{ $call->id }}/process" id="process-form">
    @csrf
    <button type="submit" id="process-btn">Process Call</button>
</form>
<div id="processing-msg" style="display:none">
    <span class="spinner"></span>
    Processing... Whisper is transcribing locally, then Claude reads it.
    This takes 60-90 seconds for a 5-minute call. Don't navigate away.
</div>

<script>
document.getElementById('process-form').addEventListener('submit', () => {
    document.getElementById('process-btn').disabled = true;
    document.getElementById('processing-msg').style.display = 'block';
});
</script>
```

## First-run notes for the Engineer

The first time `transcribe.py` runs, faster-whisper downloads the `small` model from HuggingFace. This adds ~30 seconds and ~460MB. To pre-pull on the OptiPlex before Monday:

```bash
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
```

Run that once after install. Subsequent transcriptions are fast.

## Performance expectations

Rough benchmarks for OptiPlex 9020 MT class hardware (4-core Haswell CPU, no GPU, 32GB RAM). Real numbers may vary ±50% based on exact CPU and audio characteristics:

| Audio length | faster-whisper small | Total pipeline |
|---|---|---|
| 1 minute | ~10-15 seconds | ~25-30 seconds |
| 5 minutes | ~45-60 seconds | ~75-90 seconds |
| 15 minutes | ~2-3 minutes | ~3-4 minutes |

Memory: faster-whisper uses ~1.5GB peak with int8 quantization on `small`. 32GB OptiPlex has zero issue running this alongside Laravel.

## Failure modes and recovery

- **Recording not yet uploaded to Twilio:** the recording webhook may take 30-60 seconds after hangup, sometimes longer. If user clicks "Process" too early, `recording_url` is null. UI should hide the Process button until the recording webhook fires (refresh the page or display a "Recording pending..." state).
- **Network hiccup during download:** retry once. If still failing, leave recording_local_path null and show error.
- **Whisper subprocess crashes:** rare but possible (out-of-memory on huge files). Show error, leave transcript null. User can retry.
- **Claude API rate limit:** unlikely at this volume but possible. The `Http::retry(2, 1000)` in the code handles 429s with exponential backoff.
- **Empty transcript:** if the recording is silent or Whisper produces nothing, treat as a failure. Don't send empty transcript to Claude.

## Cost expectations

faster-whisper local: $0
Claude API per call:
- Input: ~3000 tokens (skill prompt ~2000 + transcript ~1000 for 5min call)
- Output: ~800 tokens
- At Sonnet pricing (~$3/M input, ~$15/M output): ~$0.02 per call
- At 22 work days × 10 calls/day = 220 calls/month × $0.02 = ~$4-5/month

## Out of scope for Phase 1

- Speaker diarization (separating "you" from "them" in transcript) — faster-whisper outputs flat text. Phase 2 could use pyannote or Twilio's stereo channels to split.
- Real-time / streaming transcription — Phase 1 is post-call only
- Queue-based async processing — synchronous is fine for one user processing calls in sequence
- Cost tracking per call — Phase 2 settings tab feature
- Multiple frameworks per call (parallel comparison) — Phase 2
