"""Orchestrator: sweep queue -> Maps -> dedup -> Sonnet qualify -> scrub -> sink.

Run:  python run.py   (see README for env setup)

Code runs the pipeline; the model only judges one lead at a time."""
import maps
import dedup
import qualify
import scrub
import sink
import slices
from config import SLICES_PER_RUN, MAX_PER_SLICE, WORKED_OUT_RATIO


def _city_state(address: str) -> str:
    # "123 Main St, Melrose Park, IL 60160, USA" -> "Melrose Park, IL"
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 3 and parts[-2]:
        return f"{parts[-3]}, {parts[-2].split()[0]}"
    return address


def run():
    conn = dedup.connect()
    keepers, review = [], []
    productive = 0   # slices that yielded callable leads — the run target
    attempted = 0    # every slice actually swept — bounds Maps spend

    for metro, corridor, category, query, slice_id in slices.all_slices():
        # Target SLICES_PER_RUN productive slices, but cap total sweeps so a
        # dead stretch of the queue can't burn unlimited Maps calls in one run.
        if productive >= SLICES_PER_RUN or attempted >= SLICES_PER_RUN * 3:
            break
        if dedup.slice_done(conn, slice_id):
            continue
        attempted += 1

        candidates = maps.search(query, MAX_PER_SLICE)
        if not candidates:
            # Empty is not the same as mined out — it may be a bad query or a
            # Places hiccup. Park it; slice_done frees it after the rest window.
            dedup.mark_slice(conn, slice_id, "empty")
            continue

        dropped = 0  # dupes + no-phone + rejects + dead numbers

        for lead in candidates:
            lead["category"] = category
            lead["city_state"] = _city_state(lead["address"])

            if not lead["phone"]:            # guide: no phone -> drop
                dropped += 1
                continue
            if dedup.is_seen(conn, lead):    # already sourced (keep or reject)
                dropped += 1
                continue

            try:
                verdict = qualify.qualify(lead)
            except Exception as e:
                # One bad API call must not kill the run mid-slice with
                # unsaved keepers. The lead goes to the human queue instead.
                verdict = {"decision": "review", "confidence": "L",
                           "note": f"qualify failed ({type(e).__name__}) - judge by hand"}
            dedup.record(conn, lead, slice_id, verdict["decision"], verdict["confidence"])
            if verdict["decision"] == "reject":
                dropped += 1
                continue

            status = scrub.check(lead["phone"])
            dedup.mark_number(conn, lead["phone"], status)
            if status == "dead":
                dropped += 1
                continue

            (review if verdict["decision"] == "review" else keepers).append((lead, verdict))

        # A slice that came back mostly dupes/rejects is mined out.
        result = "worked-out" if dropped / len(candidates) >= WORKED_OUT_RATIO else "productive"
        if result == "productive":
            productive += 1
        dedup.mark_slice(conn, slice_id, result)

    # Order keepers H -> M -> L.
    rank = {"H": 0, "M": 1, "L": 2}
    keepers.sort(key=lambda kv: rank.get(kv[1]["confidence"], 3))

    csv_path = sink.write_csv(keepers, review)
    sink.append_sheet(keepers, review)

    print(f"Done. {len(keepers)} callable leads, {len(review)} to review "
          f"({productive} productive slices, {attempted} swept).")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    run()
