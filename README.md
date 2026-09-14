# Cutting Room

**English** | [中文](README.zh-CN.md)

A coding-agent skill for film editing. It does three things. It inventories your footage, cuts a timeline in DaVinci Resolve, and then grades its own work against a standard that does not let it be polite.

What it hands back is an edited timeline. Rendering is not its job.

## Install

There is nothing to build. Clone it somewhere Codex already looks and you are done. If you would rather not think about paths, one command handles it.

```bash
curl -fsSL https://raw.githubusercontent.com/Maoxintao98/cutting-room/main/install.sh | bash
```

The script clones the repo, checks that `SKILL.md` is intact, marks the helper scripts executable, and tells you if ffmpeg is missing. It installs to `~/.agents/skills/cutting-room`, which applies to every project you work in.

Doing it by hand works just as well.

```bash
# For yourself, in every project
git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room

# For one repository only
git clone https://github.com/Maoxintao98/cutting-room <your-repo>/.agents/skills/cutting-room
```

Nothing needs restarting. Invoke it as `$cutting-room`, or skip the command and just say what you want. Tell it "review this cut" and it picks itself up.

## Four things it does

| Mode | Your situation | What you get |
|---|---|---|
| Cut | You have the footage and no idea where to begin | It settles what kind of film this is first, then names the technique priorities for that kind |
| Execute | The plan exists; the timeline does not | Real edits in DaVinci Resolve, through its official MCP |
| Review | The cut is done, you have stared at it too long, and asking a colleague feels awkward | Scores on six dimensions, every issue pinned to a timecode, and a verdict of ship, fix, or rebuild |
| Select | Forty generated clips and no way to choose | A three-tier defect taxonomy plus a keep, fix, or discard decision tree |

The first row deserves a note. Before it cuts anything, it works out what kind of film this is. A brand mood piece and a narrative short often want opposite techniques, and cutting before you know which one you are making wastes the work.

## The eight rules

Reviewing is hard for two reasons. One is not daring to say the thing. The other is saying it carelessly. These rules exist to prevent both.

1. **No flattery, no softening.** Openers like "overall it's solid, but..." are banned. The verdict does not change because of who made the film. Calling something a rebuild job is part of the work, not a breach of manners.
2. **No padding.** Never invent a problem to look thorough. If nothing is wrong, say so. The reverse holds too, so do not manufacture praise for symmetry. Forced balance is its own kind of dishonesty.
3. **Every claim carries evidence.** If you cannot point at a timecode or a shot number, do not write it. Words like *stunning* and *great energy* add nothing.
4. **Separate fact, consensus, and taste.** A personal preference has to be marked as one. Passing taste off as a standard is the most common failure in review work.
5. **Hold strengths and weaknesses to the same bar.** A strength must be as specific as a critique, and the review must name the single best shot in the film and explain why it works. If the film is good, say so plainly, with no "but" hanging off it.
6. **Criticise the work, not the maker.** That is not the same as going easy on it.
7. **"This doesn't work" arrives with a why and a suggestion.** A rejection with no path forward is not a review.
8. **Say when you don't know.** Missing the brief, the target platform, or a hard client requirement? Name the gap instead of inventing a confident-sounding verdict.

## What a review looks like

Below is a fictional 25-second brand film.

```
Title/version: demo-v1    Type: brand film    Length: 25s    Aspect: 16:9
[Missing] target platform. This affects any judgement about safe areas.
────────────────────────────────────────────────
1. What works
   1. Best shot in the film, at 00:12. The push-in as the water falls
      continues the rotation of the previous shot, the only genuine
      motion match cut in the piece.
   2. The 0.8s of silence at 00:06 is motivated. An action triggers it
      and pulls attention back to the image.
   3. Colour temperature is consistent throughout.

2. Six dimensions
   1 Narrative progression      1/3   00:03 no causal link to what surrounds it
   2 Sound and image            2/3   00:18 flat music level, no build to the peak
   3 Composition and graphics   1/3   00:09 caption sits across a face
   4 Shot-to-shot continuity    2/3   00:07 hard cut from wide to close-up
   5 Message and brand          1/3   what is being sold is unclear
   6 Rhythm and pacing          2/3   00:15 speed ramp runs against the next shot

3. Issues, ordered by cost against benefit
   1. [High benefit, low cost]  00:18 lift the final music section by 4dB
   2. [High benefit, low cost]  00:03 cut the shot, the film reads clearer
   3. [High benefit, high cost] 00:05-09 subject consistency needs a regen

4. Verdict
   [ ] ship    [x] fix (music build, cut at 00:03, regen 00:05-09)
   In one line. Every shot works alone. Together, they do not feel like
   one film.
```

Look at the third block. Issues are ordered by **what a fix costs against what it buys, not by severity**. A large problem that takes ten seconds is worth more of your attention than a small one that needs a reshoot.

## Where it comes from

A distillation of 24 books, 19 research papers, and 27 articles, roughly 12 million characters of extracted text.

The books run the length of the editing tradition, from montage through realism. The papers cover 2023 to 2026 work on evaluating generated video. The skill folds all of it into one method and carries no citations in its own text.

## Contents

```
SKILL.md                        Main body and routing
agents/openai.yaml              UI metadata
references/
  craft.md                      Cutting: terminology, priorities, cut points, rhythm, sound, montage, transitions, blocking
  resolve.md                    Executing: the Resolve MCP, its tool contract, and nine pitfalls found in practice
  review.md                     Reviewing: the discipline, a three-pass method, the six-dimension rubric, report template
  clip-qc.md                    Selecting: a three-tier defect taxonomy, per-clip record sheet
scripts/
  probe.py                      Inventory a media folder with ffprobe
  resolve_mcp.py                Talk to the Resolve MCP over stdio
  run_step.py                   Execute a step script inside Resolve
  steps/00_inspect_timeline.py  Check a timeline before handing it over
```

Only `SKILL.md` loads on trigger. The rest is read when the task calls for it. Reviewing will not pull in the clip-selection reference.

## Verified in practice

The pipeline has been run end to end on real media, from inventorying a folder of 52 clips through creating a project, importing, building a timeline, and reading it back.

The nine pitfalls in `references/resolve.md` were not guessed. Each one cost time in a real session, including the fact that a Resolve timeline starts at frame 86400 rather than zero, which you only discover by running it.

## License

MIT
