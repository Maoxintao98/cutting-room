# Timeline inspection. Run via scripts/run_step.py, inside the sandbox, no imports.
#   python3 scripts/run_step.py scripts/steps/00_inspect_timeline.py
# Run this before handing a timeline over: check for true gaps, overruns and
# unexpected track contents.

result = {"tracks": [], "problems": [], "notes": []}

tl = project.GetCurrentTimeline()
if tl is None:
    result["error"] = "no current timeline"
else:
    fps = float(tl.GetSetting("timelineFrameRate") or 24)
    start, end = tl.GetStartFrame(), tl.GetEndFrame()
    result["name"] = tl.GetName()
    result["fps"] = fps
    result["start_frame"] = start
    result["end_frame"] = end
    result["duration_sec"] = round((end - start) / fps, 2)

    for kind in ("video", "audio"):
        try:
            count = tl.GetTrackCount(kind)
        except Exception:
            count = 0
        for i in range(1, count + 1):
            items = tl.GetItemListInTrack(kind, i) or []
            if not items:
                if kind == "video":
                    result["notes"].append(f"{kind} track {i} is empty; delete it unless it is needed")
                continue

            clips, transitions, spans = [], [], []
            for it in items:
                s, e = it.GetStart(), it.GetEnd()
                t = it.GetType()
                entry = {"name": it.GetName(), "start": s, "end": e,
                         "sec": round((e - s) / fps, 2)}
                if t == "transition":
                    transitions.append(entry)
                else:
                    clips.append(entry)
                spans.append((s, e))

            # Merge intervals: only regions covered by no clip at all count as gaps
            spans.sort()
            holes = []
            reach = spans[0][1]
            for s, e in spans[1:]:
                if s > reach:
                    holes.append({"at": reach, "frames": s - reach,
                                  "sec": round((s - reach) / fps, 2)})
                reach = max(reach, e)

            row = {"kind": kind, "index": i, "clips": len(clips),
                   "transitions": transitions, "clips_detail": clips}
            if holes:
                row["gaps"] = holes
                # The main picture track (video 1) must be continuous; other tracks may be sparse
                if kind == "video" and i == 1:
                    result["problems"].append(f"gap on the main picture track {holes}")
                else:
                    result["notes"].append(
                        f"{kind} track {i} has {len(holes)} gap(s); allowed on overlay and audio tracks"
                    )
            if reach > end:
                result["problems"].append(f"{kind} track {i} overruns the end by {reach - end} frames")
            result["tracks"].append(row)

    result["summary"] = {
        "video_clips": sum(t["clips"] for t in result["tracks"] if t["kind"] == "video"),
        "transitions": sum(len(t.get("transitions") or []) for t in result["tracks"]),
    }
