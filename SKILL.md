---
name: cutting-room
description: 剪辑、审片与 AIGC 选片（film editing, review, and AIGC clip QC）。四种用法，定方案、执行剪辑、审片、选片。Plan a cut by settling the film type, the single goal, and where to cut. Cut by building and editing the timeline in DaVinci Resolve. Review a finished cut with an honest, evidence-based critique, six-dimension scoring, and a ship/fix/rebuild verdict. Select by judging whether AIGC-generated clips are usable (KEEP/fix/NG) and ranking them. Use when cutting or diagnosing an edit, driving DaVinci Resolve to assemble a timeline, reviewing a finished cut and needing an honest critique, judging whether AI-generated footage is usable, scoring or ranking generated shots, or doing shot-by-shot analysis.
---

# Cutting, Reviewing, and Selecting

From "what do I have" through to "what do I hand over". Four modes share one set of judgements.

| Mode | When | Detail |
|---|---|---|
| **Plan** (定方案) | Settle the film type, the goal, and where to cut | [references/craft.md](references/craft.md) |
| **Cut** (执行剪辑) | Actually build the timeline | [references/resolve.md](references/resolve.md) |
| **Review** (审片) | Given a finished cut, produce a precise, evidence-based judgement | [references/review.md](references/review.md) |
| **Select** (选片) | Judge a single AIGC clip and rank a batch | [references/clip-qc.md](references/clip-qc.md) |

Scripts: `scripts/probe.py` inventories media, `scripts/resolve_mcp.py` talks to Resolve directly.

---

## 1. Before you start: settle what kind of film this is

**Do not start cutting.** Ask first. Different film types often want opposite techniques.

### Six questions (ask whichever are missing)
1. **Type and purpose**: brand mood piece / product film / narrative short / documentary·interview / talking head·explainer / beat-driven·music video / action·sport?
2. **Length and aspect**: 15s or 30s+? Landscape or vertical (vertical needs safe margins)?
3. **Desired effect**: emotional impact / clarity of information / selling / storytelling. **Only one primary goal.**
4. **Footage**: shot or generated? What proportion is usable? Any known defects?
5. **Tone and reference**: is there a reference film? Is the brand restrained or loud?
6. **Sound**: is there music, voice-over, or effects?

**Communication discipline**: ask only the two or three most critical questions at a time, never dump the whole list. If the user says "use your judgement", take the safest default: **clarity first, emotion second**.

### Film type against technique priority

| Type | Prioritise | Beware |
|---|---|---|
| Brand mood piece | Montage, physical rhythm, colour consistency, cutting on the beat with room to breathe | Do not force a narrative arc; avoid showy transitions |
| Product film | Information clarity, inserts, action sounds, eye-trace | Technique that outshines the product |
| Narrative short | Continuity, reaction shots, eyeline match, **emotional cut points (情绪剪接点)** | Jump cuts break immersion |
| Documentary·interview | Sound bridges, J/L cuts, inserts to cover jump cuts | Do not cut on heavy beats |
| Talking head·explainer | J cuts, jump cuts, captions, **rhythmic cut points (节奏剪接点)** | Long static shots lose the viewer |
| Beat-driven·music video | Rhythmic cut points, motion match cuts, speed ramps | Cutting on every beat turns it into MTV |
| Action·sport | Motion-to-motion cutting (动接动), extreme scale contrast (两极镜头), speed ramps | Crossing the axis disorients the viewer |
| Realist·long take | **Straight-cut editing (无技巧剪辑)**, staging in depth, continuous sound | Optical effects break the realism |

### Two stylistic routes

- **Montage (constructive).** Meaning is produced *between* shots, and the edit is an active author. Suits expression, persuasion, emotional peaks, compressed time.
- **Realism (observational).** Respect the continuity of time and space; the edit only has to avoid interrupting. Suits texture of life, performance, pressure and waiting.

Which one you take depends on whether you are **persuading** or **presenting**. Both produce good films, but the techniques fight each other. Do not bet on both in one piece.

## 2. Step one: inventory the footage

**Know your hand before you play it.** Run an inventory and turn "what footage is there" from an impression into a comparable table.

```bash
python3 scripts/probe.py <media-directory>
python3 scripts/probe.py <media-directory> --contact 6   # also prints contact-sheet commands
```

The output lists duration, resolution, frame rate, orientation, codec, audio tracks and size for every clip, and flags anomalies (no audio, off-spec frame rate, vertical that needs safe margins).

**To see content, extract frames.** The inventory answers "what are the specs", not "what is in it". To judge content, motion and head/tail frames, generate a contact sheet with the ffmpeg command the script prints.

Then do one classification: **separate generation defects from editing problems.** The same awkwardness can come from either, and the cure is opposite.

- **Generation defect.** The model drew the frame wrong (hands, text, physics). Regenerate, patch, mask it, or cut it out.
- **Editing problem.** The footage is fine; the cut point, the order, the sound or the rhythm is wrong. Fixing the cut saves it, no regeneration needed.

Aesthetic quality and editing-technique execution are only **weakly correlated**. A beautiful-looking film can still be cut wrong. Classify before you diagnose.

## 3. Step two: settle the plan (cut points and rhythm)

### The six rules: arbitration order when cut points conflict

An ideal cut point satisfies six things at once. **When they conflict, hold from the top down and sacrifice from the bottom up.**

| Priority | Rule | Weight | Question |
|---|---|---|---|
| 1 | Emotion | 51% | Is it true to the emotion of the moment? |
| 2 | Story | 23% | Does it advance the narrative? |
| 3 | Rhythm | 10% | Does it land on the right beat? |
| 4 | Eye-trace | 7% | Is the audience's attention carried smoothly? |
| 5 | Two-dimensional plane of screen | 5% | Does it hold the 180° axis and screen direction? |
| 6 | Three-dimensional space of action | 4% | Does it preserve the actual spatial relationship? |

**The mechanism most people miss.** Satisfying a higher rule **masks** problems with lower ones, and not the other way round. Get emotion and story right and nobody minds that you crossed the axis. Get the axis right but ignore eye-trace, and the cut fails.

**The corollary.** Sacrificing spatial continuity for accurate emotion is a professional judgement, not a mistake. It is also where jump cuts get their legitimacy. Running the six rules backwards (everything for the sake of not crossing the axis, keeping the image smooth) is the signature failure of amateur editing: technically correct, emotionally empty.

**A supporting intuition.** The blink theory. People blink at the moment their thought turns, so a good cut point sits roughly where the audience would blink. Watch the film repeatedly; wherever you drift off at the same spot every time is where the cut should or should not be.

### Four questions before every cut

1. **What is being cut to.** What **new information** does the audience get after this cut? A shot with no new information is a dead shot.
2. **Why cut.** Does the narrative advance, does the emotion turn, does the rhythm need it? A cut with no reason is cutting for its own sake.
3. **When to cut.** Precise to the frame. An action cut goes at the **middle of the movement**, not after it finishes. An emotional cut can be held long or cut off early. A rhythmic cut lands on the beat.
4. **How to cut.** Hard cut is the default, nine times out of ten. Dissolves, wipes, jump cuts and match cuts each carry a tonal cost. The transition must fit the register: a wipe in a luxury ad reads as cheap.

**Motion-to-motion and static-to-static (动接动·静接静).** Motion cutting to motion needs the head and tail of the camera move preserved, so the outgoing movement carries the incoming shot. Static cutting to static: the stillness of the outgoing shot is what the incoming shot leans on. A mixed join needs a bridging point, supplied by an entrance or exit, an occlusion, movement in the same direction, or sound arriving first.

Glossary, the cut-point system, the three-layer rhythm model, the sound checklist, montage and transitions, camera axis, and the shot-by-shot sheet are all in [references/craft.md](references/craft.md).

## 4. Step three: land it in Resolve

The plan becomes a timeline. This runs through the official MCP shipped with DaVinci Resolve 21.1.

**The deliverable at this stage is an edited timeline. Rendering is not your job.**

```bash
python3 scripts/resolve_mcp.py status                     # is Resolve running
python3 scripts/run_step.py steps/10_picture.py           # run one step script
python3 scripts/run_step.py steps/30_titles.py --unsafe   # when filesystem access is needed
```

**Three hard rules**

1. **Look it up before you write it.** Confirm the signature with `search_scripting_api` before calling it. Never write an API from memory.
2. **Never overwrite the user's project.** Save as a new project or a new timeline before starting.
3. **Report before large changes.** Explain what you are about to do before deleting clips, restructuring, running bulk operations, or starting a render.

The flow is: inventory, create the project, import, build the timeline, cut, add overlays, handle sound, inspect.

**Run the timeline inspection before handing over.** It reports clip and transition counts per track and any true gaps. The main picture track must be continuous; overlay, title and audio tracks are allowed to be sparse.

```bash
python3 scripts/run_step.py scripts/steps/00_inspect_timeline.py
```

API list, script skeleton, and the division of labour with ffmpeg are in [references/resolve.md](references/resolve.md).

## 5. Step four: self-check and review

Use this after finishing a cut, or when the user hands you a finished film to review.

### The six-dimension scorecard

Score each from 0 to 3 (0 no problem / 1 minor / 2 clear / 3 fatal).

| # | Dimension | Questions |
|---|---|---|
| 1 | Narrative progression | Do the shots belong to one story? **Can the order be reversed?** Is there an establishing shot or a hook at the start? Is the ending abrupt? |
| 2 | Sound and image working together | Cut on the beat, action sounds matching, sound bridges, does the music have an energy arc, is the silence motivated? |
| 3 | Composition and graphics | Framing (subject cropped or too near the edge), eye-trace, captions (across a face? enough contrast?), colour consistency |
| 4 | Shot-to-shot continuity | Does motion carry across, are the environments compatible (light direction, colour temperature), does the transition fit the register |
| 5 | Message and brand coherence | After watching, do you know what is being sold? Or is it "a set of unrelated footage"? |
| 6 | Rhythm and pacing | Do shot count and length match the target energy? Are speed changes motivated and pointed the right way? |

**The three most common failures** (check these first): motion that does not carry between shots / unclear information / **an order that can be reversed** (if it plays the same backwards, the sequence has no narrative logic).

### The discipline of objectivity

The floor for reviewing is saying the true thing accurately.

1. **No flattery, no softening.** Banned: "overall it's solid, but…", "the flaws don't outweigh the merits", "just a small suggestion". The verdict does not change because of who made the film. If it needs rebuilding, say so. **Offending someone is the cost of this work, not a mistake.**
2. **No padding.** Do not invent a problem to look thorough; if nothing is wrong, say nothing is wrong. The reverse holds too: do not manufacture strengths for symmetry. Forced balance is its own kind of dishonesty.
3. **Every judgement carries evidence.** Only write what you can point at with a timecode or shot number. Words like stunning, premium, textured and well-paced score nothing. They are noise.
4. **Separate fact, consensus and preference.** A personal preference must be marked [preference] and cannot serve as a criterion. Passing preference off as a standard is the most common failure in review work.
5. **One standard for strengths and weaknesses.** A strength must be as specific as a criticism, and must name the single best shot in the film and say why it works. When a film is good, say so plainly, without a "but" that weakens it.
6. **Judge the work, not the person.** Not judging the person does not mean going easy. Be as severe with the work as it deserves.
7. **A criticism arrives with a why and a fix.** Rejecting without a path is not a review.
8. **Say when you do not know.** Missing brief, missing platform, missing hard requirement? Say so. Do not invent a confident-sounding verdict.

The process is three passes. First pass with no pen, noting only the seconds where you drifted or were caught. Second pass with a pen, breaking the film down shot by shot. Third pass with the sound off, then with only the sound, because sound problems are the easiest to mask by picture.

Report template, sub-item definitions and verdict criteria are in [references/review.md](references/review.md).

## 6. Selecting: judging a single generated clip

Tag every **single AIGC clip** on two independent axes.

- **Layer A · generation realism.** Are there defects? Grade them in three tiers (surface / structural / temporal-semantic).
- **Layer B · editing usability.** Assuming the defects were fixed, is it a good piece of material? Look at **motion**: dead, directional, or with a clear head and tail. Motion decides what role the clip can take.

The two axes are independent. A clip can fail A and pass B (broken image, beautiful motion, worth regenerating), or pass A and fail B (flawless but motionless, unusable next to anything).

**Handling the three defect tiers**

- Tier 1 (surface: colour shift, flicker, texture, abnormal camera motion). Inside the focal area, regenerate. Outside it, grade, denoise or shorten the shot.
- Tier 2 (structural: deformation, merged objects, anatomical violations, failed occlusion). Inside the focal area, regenerate. Outside it, crop or mask.
- Tier 3 (temporal-semantic: **irreversibility violations**, broken causality, action without consequence, unreadable text, broken cross-shot consistency). The most damaging; most of these must be regenerated. The viewer cannot name what is wrong but will feel it as fake.

**Naming discipline.** Put the status in the filename, `number_content_status_note`. Do not delete NG material; the failures for a given prompt are the evidence for the next prompt revision.

The 30 fine-grained labels, the per-clip record sheet and the closed-loop workflow are in [references/clip-qc.md](references/clip-qc.md).

## 7. Remedies

Try these in order, cheapest first.

1. Move the cut point or shorten the shot, cutting out the defective frames
2. Mask it: a foreground element, a caption, a transition
3. Crop and reframe to exclude defects outside the focal area
4. Grade for consistency, to rescue environmental continuity and colour temperature jumps
5. Cover it with sound
6. Change speed, stretching two seconds into four so the model has less to animate
7. Regenerate, changing **one prompt variable at a time**, and compare

## 8. Discipline

- **Cut your favourite shot.** If it serves you and not the film, delete it.
- **Accept some discontinuity.** Technical imperfection is not the same as a mistake.
- **Sound is equal to picture.** Cut the sound separately, then check it against the picture.
- When the cut is done, walk the checklist at the end of [references/craft.md](references/craft.md).
