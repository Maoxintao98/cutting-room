# Executing · DaVinci Resolve

Once the judgements are made, build the timeline. This runs through the official MCP shipped with DaVinci Resolve 21.1.

**The deliverable is an edited timeline.** Rendering is the user's to run.

## Two ways in

**A. When the MCP tools are available (preferred).**
Once Codex has `davinci_resolve` mounted as MCP tools, call them directly.

| Tool | Purpose |
|---|---|
| `run_script` | Sandboxed Python with access to the DaVinciResolveScript API |
| `run_script_unsafe` | Same, plus filesystem, network and subprocess access |
| `search_scripting_api` | Search API types and functions by keyword |
| `get_scripting_api` | Pull the full declaration of a given type |
| `get_scripting_docs` | Developer documentation |
| `get_resolve_status` / `launch_resolve` | Check state, launch Resolve |
| `update_dctl` / `generate_lut` / `list_luts` and others | LUT and DCTL management |

**B. When the MCP tools are not mounted (fallback).**
`scripts/resolve_mcp.py` talks to the same server directly, with identical capability.

```bash
python3 scripts/resolve_mcp.py status              # is Resolve running
python3 scripts/resolve_mcp.py search Timeline     # look up API
python3 scripts/resolve_mcp.py run cut.py          # execute a script
```

## The tool contract (read before writing any script)

`run_script` and `run_script_unsafe` have a few hard requirements. Getting any of them wrong returns "script completed with no output or result", with no error.

| Requirement | Detail |
|---|---|
| The parameter is `script` | Not `code`. Getting the name wrong raises no error, it just silently returns nothing |
| Injected variables | `resolve` and `project` are ready to use. Do not fetch them yourself |
| Returning data | Assign structured output to `result`. Anything `print()` emits is captured too |
| Timeout | 10 seconds by default, **60 seconds maximum**. Long work has to be split into steps |
| Sandbox limits | `run_script` blocks `os`, `sys`, `pathlib`, `shutil` |

Use `run_script_unsafe` when you need the filesystem or a subprocess. Use `run_script` for everything else.

**Three scripts come with this skill**, all under `scripts/`.

```bash
python3 scripts/resolve_mcp.py status          # is Resolve running
python3 scripts/run_step.py steps/10_picture.py            # run in the sandbox
python3 scripts/run_step.py steps/30_titles.py --unsafe    # with filesystem access
python3 scripts/run_step.py steps/30_titles.py --pre lib/titles.py lib/common.py
```

`run_step.py --pre` works around the sandbox having no imports: shared code is concatenated into the script text before it is sent.

A step script does one thing and returns through `result`.

```python
result = {"project": project.GetName()}
tl = project.GetCurrentTimeline()
if tl:
    result["timeline"] = tl.GetName()
    result["end_frame"] = tl.GetEndFrame()
```

## Three hard rules

**1. Look it up before you write it.** Confirm the signature with `search_scripting_api` before calling anything. Never write an API from memory; it changes between versions and a recalled signature is usually stale. Looking it up costs seconds. Getting it wrong costs a rerun.

**2. Never overwrite the user's project.** Save as a new project or a new timeline before starting, and leave the original untouched. The user's project may hold manual grades and cuts.

**3. Report before large changes.** Explain what you are about to do before deleting clips, restructuring, running bulk operations, or starting a render. The cost of saying it is far below the cost of getting it wrong.

## Execution pipeline

```
1 Inventory    python3 scripts/probe.py <media-directory>
2 Project      Open or create a project, set timeline resolution and frame rate
3 Import       MediaPool.ImportMedia
4 Timeline     MediaPool.CreateTimelineFromClips / Timeline.AddTrack
5 Cut          AppendToTimeline / DeleteClips / SetClipsLinked
6 Overlays     Captions and graphics go through Fusion comps, in a separate pass
7 Sound        NormalizeAudioLevel / AutoAlignClips
8 Inspect      scripts/steps/00_inspect_timeline.py
9 Hand over    Report the timeline state; rendering goes to the user
```

## Timeline self-check

**Run the inspection before handing over.** It merges intervals to work out coverage, so only regions genuinely uncovered by any clip count as gaps. A transition sitting over two clips is not misreported.

```bash
python3 scripts/run_step.py scripts/steps/00_inspect_timeline.py
```

The output covers frame rate, duration, clip and transition counts per track, and gap positions. Two rules for reading it.

**The main picture track (video 1) must be continuous.** A gap there is a problem. Overlay, title and sound-effect tracks are allowed to be sparse; an unfilled track is not an error.

**Anything extending past the timeline end is a real problem** and gets reported on any track.

It also flags empty video tracks, which can be deleted.

## Verified API (21.1)

**Getting the objects**

```python
resolve  = dvr_script.scriptapp("Resolve")
project  = resolve.GetProjectManager().GetCurrentProject()
pool     = project.GetMediaPool()
timeline = project.GetCurrentTimeline()
```

**Media and timeline**

| Call | Effect |
|---|---|
| `MediaPool.ImportMedia(clipInfos)` | Import files or folders into the current media pool folder |
| `MediaPool.CreateTimelineFromClips(name, clipInfos)` | Create a timeline from clips |
| `MediaPool.AppendToTimeline(clipInfos)` | Append clips to the current timeline |
| `Timeline.AddTrack(trackType, subTrackType)` | Add a track |
| `Timeline.DeleteClips(items, rippleDelete)` | Delete clips, optionally ripple |
| `Timeline.SetClipsLinked(items, linked)` | Link or unlink video and audio |
| `Project.SetCurrentTimeline(timeline)` | Switch the current timeline |
| `Project.GetTimelineByIndex(idx)` | Get a timeline by index |

**Sound**

| Call | Effect |
|---|---|
| `Timeline.NormalizeAudioLevel(items, options)` | Normalise audio level |
| `Timeline.AutoAlignClips(items, options)` | Align clips automatically |

**Export and render** (rendering is the user's responsibility; listed for reference)

Timeline export types are `resolve.*` constants. Verified to exist: `EXPORT_EDL`, `EXPORT_FCPXML_1_8`, `EXPORT_FCPXML_1_9`, `EXPORT_FCPXML_1_10`, `EXPORT_AAF`, `EXPORT_DRT`, `EXPORT_OTIO`, `EXPORT_ALE`.

Render calls include `Project.StartRendering(jobIds)`, `Project.IsRenderingInProgress()` and `Project.GetRenderJobList()`, with `ExportVideo`, `ExportAudio`, `ExportAlpha` and `ExportSubtitle` among the render settings.

The exact method names for export and render change between versions. **Look them up with `search_scripting_api` before use.**

## Script skeleton

Inside the sandbox, `resolve` and `project` are already injected. Do not fetch them, and do not import anything.

```python
# steps/10_picture.py
# run with: python3 scripts/run_step.py steps/10_picture.py
result = {}

pool = project.GetMediaPool()
items = pool.ImportMedia(["/path/to/media-directory"])
result["imported"] = len(items)

timeline = pool.CreateTimelineFromClips(
    "cut_v1", [{"mediaPoolItem": i} for i in items]
)
project.SetCurrentTimeline(timeline)
result["timeline"] = timeline.GetName()
result["end_frame"] = timeline.GetEndFrame()
```

Three conventions: one thing per step, return through `result`, and on failure write the error into `result` rather than raising.

When you need to read a script file, write a log, or call ffmpeg, use `run_script_unsafe` and concatenate the shared code in with `--pre`.

## Dividing labour with ffmpeg

Resolve handles project-level cutting, grading, sound and delivery. ffmpeg handles what it is poor at.

- Media inventory (`scripts/probe.py`)
- Frame extraction to see content, building contact sheets
- Fast transcoding, proxy generation, audio extraction
- Checking the finished render: duration, audio tracks, resolution

The two work in sequence: use ffmpeg to survey the footage, go into Resolve to build the project, then use ffmpeg again to verify the output.

## Pitfalls found in practice

Every one of these came out of driving Resolve for real. They determine how you write the script and what order you debug in.

**1. The sandbox has no filesystem.**
`run_script` cannot read files and cannot import local modules. Use `run_script_unsafe` when you need file access or a subprocess. Shared code cannot be imported, so concatenate its source into the script before sending it.

**2. Appending clips and attaching Fusion comps are two separate calls.**
The objects returned by `AppendToTimeline` in that moment cannot host a Fusion comp. Doing both in one script returns None for all of them. Correct approach: run once to append only, then run again to fetch the clips and attach the comps.

**3. A missing font crashes the render outright.**
The error looks like `Font Not Found: PingFang SC Bold`. Fusion defaults to a Bold face that the system may not have. Query the font list before setting `Font`.

```python
fusion = resolve.Fusion()
fonts = fusion.FontManager.GetFontList()   # FontManager is a property, not a method
names = list(fonts.keys())                 # use a name that actually exists
```

Writing `fusion.FontManager()` returns None, and then reports an error that has nothing to do with fonts.

**4. A render can fail part-way without saying so.**
`StartRendering` returning True only means the job was submitted. Poll `GetRenderJobStatus` for `JobStatus` and note where `CompletionPercentage` stops. When it finishes, verify the frame count with ffprobe. A count clearly below duration times frame rate means it did not render through.

**5. `ExportCurrentFrameAsStill` is unreliable.**
It can return None repeatedly, and whether Resolve is in the foreground or which page it is on affects it. For frame extraction, ffmpeg is steadier.

**6. Multiple sessions fight over one Resolve.**
When another session is driving the same Resolve, the script channel interrupts itself. The symptom is a mass of None returns and assorted exceptions. Confirm only one session is driving before starting.

**7. Print JSON at every step.**
Break the work into numbered step scripts, one thing each, ending with structured output. The Resolve script channel is not stable; doing too much at once leaves you nowhere to look when it fails. Writing many `probe`, `diag` and `try` steps is normal.

**8. Timelines start at 01:00:00:00.**
`GetEndFrame()` returns an **absolute frame number**. A new timeline starts at `86400`, one hour in, not at zero. Duration must be computed as `GetEndFrame() - GetStartFrame()`, or it comes out an hour too long. `scripts/steps/00_inspect_timeline.py` already handles this.

**9. Appending to an empty timeline packs clips back to back.**
When `AppendToTimeline` is called without `recordFrame`, clips are laid end to end on the first video track in order, and audio syncs automatically onto the matching audio track. Pass `recordFrame` explicitly only when you need precise placement.
