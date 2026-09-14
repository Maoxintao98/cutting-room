# 时间线体检。用 scripts/run_step.py 执行，沙箱内运行，不要 import。
#   python3 scripts/run_step.py scripts/steps/00_inspect_timeline.py
# 时间线交给用户之前跑一遍，确认没有真空隙、没有超尾、轨道内容符合预期。

result = {"tracks": [], "problems": [], "notes": []}

tl = project.GetCurrentTimeline()
if tl is None:
    result["error"] = "当前没有时间线"
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
                    result["notes"].append(f"{kind} 轨 {i} 是空的，如非必要可删")
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

            # 区间合并，只有真正没被任何片段覆盖的地方才算空隙
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
                # 主画面轨（video 1）必须连续，其余轨道有空隙是正常的
                if kind == "video" and i == 1:
                    result["problems"].append(f"主画面轨有空隙 {holes}")
                else:
                    result["notes"].append(
                        f"{kind} 轨 {i} 有 {len(holes)} 处空隙（覆盖轨与音效轨允许）"
                    )
            if reach > end:
                result["problems"].append(f"{kind} 轨 {i} 超出末尾 {reach - end} 帧")
            result["tracks"].append(row)

    result["summary"] = {
        "video_clips": sum(t["clips"] for t in result["tracks"] if t["kind"] == "video"),
        "transitions": sum(len(t.get("transitions") or []) for t in result["tracks"]),
    }
