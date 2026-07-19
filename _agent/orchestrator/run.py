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
    slices_worked = 0

    for metro, corridor, category, query, slice_id in slices.all_slices():
        if slices_worked >= SLICES_PER_RUN:
            break
        if dedup.slice_done(conn, slice_id):
            continue

        candidates = maps.search(query, MAX_PER_SLICE)
        if not candidates:
            dedup.mark_slice(conn, slice_id, "worked-out")
            continue

        slices_worked += 1
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

            verdict = qualify.qualify(lead)
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
        dedup.mark_slice(conn, slice_id, result)

    # Order keepers H -> M -> L.
    rank = {"H": 0, "M": 1, "L": 2}
    keepers.sort(key=lambda kv: rank.get(kv[1]["confidence"], 3))

    csv_path = sink.write_csv(keepers, review)
    sink.append_sheet(keepers, review)

    print(f"Done. {len(keepers)} callable leads, {len(review)} to review.")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    run()
