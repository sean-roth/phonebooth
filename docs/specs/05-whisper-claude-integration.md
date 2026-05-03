# 05 — REMOVED: Whisper Transcription Pipeline

## This spec is intentionally empty

Earlier drafts of this spec described a Whisper-based transcription pipeline that ran after every cold call: download the recording from Twilio, split the stereo file into two mono files via ffmpeg, run faster-whisper on each channel, merge the segments with speaker attribution, write the transcript markdown for Claude Desktop to coach against.

That entire pipeline was removed by spec 11 (recording pivot).

## Why

See spec 11 for the full rationale. The short version:

- Cold calls are 30-90 seconds and produce low-signal coaching data
- Recording cold calls in Illinois requires a disclosure script that adds friction and decline-rate risk
- Discovery calls are where the coaching value lives, and they happen in Google Meet (which handles consent natively)
- Removing the pipeline removes ~40% of Phase 1's complexity

## What replaced it

For cold calls: nothing. Sean's own observations in the post-call form (pain_points + notes) are the data.

For discovery calls: see spec 09. Google Meet records the conversation with platform-managed consent; Sean exports the transcript and Claude Desktop coaches against it via filesystem MCP.

## What this means for the build

The Engineer should not implement:

- `RecordingDownloader` service
- `Transcriber` service
- `ChannelSplitter` service
- `scripts/transcribe.py`
- The `/calls/{call}/process` route
- The `storage/app/recordings/` directory
- The `storage/app/coaching/transcripts/` directory (was for cold-call transcripts; replaced by `discoveries/` for discovery-call transcripts per spec 09)
- Any faster-whisper installation or ffmpeg verification

If a future Phase 2 conversation reintroduces cold-call recording (e.g., based on field testing showing it would have been valuable), this spec can be restored from git history. The commit that removed it is tagged in the message log.
