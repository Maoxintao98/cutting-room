# Cutting Room

[中文](README.zh-CN.md) | **English**

A skill library for coding agents, built on the Agent Skills open standard (SKILL.md). It covers media inventory, automated timeline editing in DaVinci Resolve, quantitative review, and QC for AI-generated footage.

`install.sh` installs to the Codex user-level directory. Other tools read their own skill directories (Cursor and Antigravity read `.agents/skills` inside a repository, Claude Code reads `~/.claude/skills`), so clone the repo into whichever one applies.

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Maoxintao98/cutting-room/main/install.sh | bash
```

The script checks for `ffprobe`, validates `SKILL.md`, marks the helper scripts executable, and installs to `~/.agents/skills/cutting-room`.

Or clone it yourself:

```bash
# Applies to every project
git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room

# Applies to one repository
git clone https://github.com/Maoxintao98/cutting-room <project-path>/.agents/skills/cutting-room
```

Invoke it with `$cutting-room`, or just state the task: "inventory this footage", "start a rough-cut timeline in Resolve", "review this cut and list the problems by timecode".

---

## Four modes

| Mode | Trigger | Deliverable | Reference |
| :--- | :--- | :--- | :--- |
| **Plan** | Footage in hand, direction undecided | Film type and a single primary goal, plus technique priorities and cutting rules | [craft.md](references/craft.md) |
| **Cut** | Plan settled, timeline needed | Project, clips, captions and audio built in DaVinci Resolve | [resolve.md](references/resolve.md) |
| **Review** | Quality check on a cut or a rough assembly | Six-dimension scores, timecode evidence, fixes ranked by cost against benefit | [review.md](references/review.md) |
| **Select** | Screening a large batch of generated clips | Three-tier defect taxonomy, routed by a keep / fix / discard decision tree | [clip-qc.md](references/clip-qc.md) |

---

## Review rules

1. **Do not soften the verdict.** Phrases like "overall it's solid, but..." and "the flaws don't outweigh the merits" are banned. The verdict is one of three: ship, fix, rebuild.
2. **Do not pad.** If there is no problem, say there is no problem. Never invent one to look thorough, and never manufacture praise for symmetry.
3. **Every judgement carries a timecode.** Precise to the second, the frame, or the shot number. Words like "premium", "textured" and "well-paced" are banned because they cannot be quantified.
4. **Separate fact, consensus and preference.** A subjective preference must be marked as such and cannot serve as a passing criterion.
5. **One standard for strengths and weaknesses.** A strength must be as specific as a criticism, and must name the best shot in the film and the craft reason it works. Do not qualify praise with a conjunction that weakens it.
6. **Judge the work only.** The assessment covers image, sound and structure. Never the person.
7. **A criticism must arrive with a solution.** Name the problem and the concrete path to fixing it, or the technical substitute.
8. **Declare information gaps.** If the brief, the target platform or a technical spec is missing, say so rather than assuming.

---

## Sample review report

```text
Title/version: demo-v1    Type: brand film    Length: 25s    Aspect: 16:9
[Missing] target platform, so vertical safe areas cannot be assessed
─────────────────────────────────────────────────────────────
1. What holds
  1. Best shot: at 00:12 the push-in as the water falls runs in the same
     direction as the previous shot's rotation (a motion match cut).
  2. At 00:06, 0.8s of silence triggered by an action pulls attention
     back to the subject.
  3. Colour temperature and contrast ratio are consistent throughout.

2. Six dimensions (0 clean / 1 minor / 2 clear / 3 fatal)
  1 Narrative progression      1/3  [00:03] no causal link to either neighbour; plays the same in reverse
  2 Sound and image            2/3  [00:18] flat music level with no build to the peak; a key action sound is missing
  3 Composition and graphics   1/3  [00:09] caption sits across a face
  4 Shot-to-shot continuity    2/3  [00:07] hard cut from wide to close-up with no bridging beat
  5 Message and brand          1/3  no core product claim established
  6 Rhythm and pacing          2/3  [00:15] speed ramp runs against the next shot's motion

3. Issues (ranked by benefit against cost)
  1. [High benefit, low cost]  00:18 lift 4dB before the music peak and add the action sound
  2. [High benefit, low cost]  00:03 cut the empty shot; tighter rhythm, denser information
  3. [High benefit, high cost] 00:05-00:09 subject deformation; regenerate with a revised prompt

4. Verdict
  [ ] ship    [X] fix (per the list above)    [ ] rebuild
  Summary: each shot passes on its own; the sequence lacks connective logic.
```

---

## Basis and standards

Built from 24 books on editing theory, 19 papers on generated-video quality assessment, and 27 industry technical specifications:

- **Cut-point arbitration**: emotion 51% > story 23% > rhythm 10% > eye-trace 7% > two-dimensional plane 5% > three-dimensional space 4%. When they conflict, hold the top and sacrifice your way up from the bottom.
- **AIGC defect taxonomy**:
  - Tier 1 (surface): colour shift, flicker, local noise.
  - Tier 2 (structural): unexpected deformation, extra limbs, clipping through occlusion.
  - Tier 3 (temporal-semantic): irreversible physical violations, broken causality, cross-shot consistency failure.

---

## Layout

```text
cutting-room/
├── SKILL.md                     # Skill entry point and workflow
├── agents/openai.yaml           # Agent metadata
├── install.sh                   # Install script
├── references/
│   ├── craft.md                 # Cutting grammar: film types, four questions per cut, rhythm model, transitions
│   ├── resolve.md               # Resolve automation: API contract, common failures
│   ├── review.md                # Review system: six-dimension rubric, three-pass method, report template
│   └── clip-qc.md               # AIGC selection: defect taxonomy, motion assessment, keep/NG decision tree
└── scripts/
    ├── probe.py                 # ffprobe scan of media metadata and anomalies
    ├── resolve_mcp.py           # DaVinci Resolve official MCP client
    ├── run_step.py              # Step-script runner for Resolve
    └── steps/
        └── 00_inspect_timeline.py # Timeline integrity: gaps, overruns, empty tracks
```

---

## DaVinci Resolve notes

- **Timeline start frame**: a Resolve timeline normally begins at `01:00:00:00`, which is frame 86400. Timecode conversion and frame arithmetic must use that as the origin.
- **Project safety**: create a new timeline or save the project under a new name before bulk operations. Never overwrite the user's original project.
- **Delivery check**: run `steps/00_inspect_timeline.py` before export to verify track continuity and catch unintended gaps.

---

## License

[MIT](LICENSE)
