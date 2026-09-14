# Selecting a Single Generated Clip · Detail

> Use this to judge whether **one AIGC-generated clip** is usable. To assess a **whole finished film**, see [review.md](review.md).

---

## 1. Defect taxonomy (three tiers / 30 types)

Tiers are set by **how much reasoning it takes to notice the defect**. The labels and definitions come from surveying failure patterns across a large body of AIGC video, distilled into 30 fine-grained types.

### Tier 1 · Surface artifacts
> Visible from local appearance alone. You see it at a glance.

**Colour and exposure**
- Colour exposure anomaly — overall colour cast, blown highlights or crushed blacks, drift
- Lighting and shadow inconsistency — light direction or hardness contradicting itself within one scene
- Baked-in lighting — the light behaves like a texture map and does not change as objects move

**Camera and lens**
- Unnatural camera motion — shake, abrupt speed changes, moves with no physical basis
- Optical failure — chaotic focus, wrong depth of field, abnormal bokeh shapes
- Refraction distortion — refraction through glass, water or transparent media that is physically impossible
- Reflection inconsistency — mirror or water reflections not matching the object, or failing to deform

**Image quality and texture**
- Inconsistent blur — sharp where it should be soft, soft where it should be sharp
- Texture inconsistency — material jumping between frames or regions
- Flickering and noise
- Oversmoothing — plastic skin, detail wiped flat

### Tier 2 · Structural defects
> Requires understanding how an object is put together.

**Identity and morphology**
- Unnatural morphing — rigid bodies warping, objects bending like rubber
- Abnormal multi-object merging or splitting
- Feature instability — a fixed property of the same object (hair, logo, button count) changing across time
- Abnormal facial expression

**Space and depth**
- Occlusion failure — what should be hidden is not hidden
- Spatial clipping — objects intersecting, cutting into one another
- Depth and perspective distortion

**Functional structure**
- Non-biological structural loss — missing parts, broken structure (half a wheel, a cup with no handle)
- Biological anatomy violation — six fingers, reversed joints, wrong proportions

**Optical consistency**: cross-frame consistency of reflection, refraction and lighting. Same family as tier 1 but needs more than one frame to judge.

### Tier 3 · Temporal-semantic violations
> Requires integrating across frames plus commonsense and causal reasoning. **The most damaging.** The viewer cannot say what is wrong but will feel it as fake.

**Motion**
- Unnatural biological motion — walking that floats, joints moving wrongly
- Identical multi-subject motion — a crowd moving like clones
- Dynamic and kinematic inconsistency — speed, acceleration or inertia breaking physics

**Causality**
- Violation of causality — A could not have caused B
- **Irreversibility violation** — a smashed glass reassembling, spilt water returning. **The most glaring of all**
- Action without consequence — a punch lands on a face and the face does not react
- Consequence without valid action — an object moves with nothing to have moved it

**Commonsense**
- Action-context mismatch — swimming in a living room
- Canonical appearance violation — a purple banana, a fire engine that is not red
- Commonsense failure

**Scene continuity**
- Spatial coherence — relative positions or points of contact contradicting themselves
- Text and symbol unreadable — signage or captions dissolving into scribble. **The classic AIGC tell**
- Object disappearance or appearance from nowhere
- Cross-shot coherence — costume, prop, hair or environment changing across a cut

### Severity against handling

| Tier | Typical handling |
|---|---|
| Tier 1 (surface) | Inside the focal area: regenerate locally. Outside it: grade, denoise, shorten |
| Tier 2 (structural) | Inside the focal area: regenerate. Outside it: crop and reframe, mask, shorten |
| Tier 3 (temporal-semantic) | Mostly regenerate. In extreme cases, cut around it and mask with a transition |

**Note**: this taxonomy is **diagnostic**, not mutually exclusive. One clip often hits several types at once, such as structural deformation plus temporal inconsistency. **Multiple labels are allowed** and a report naming several is more accurate than one naming a single label.

---

## 2. Per-clip record sheet

```
Filename:
Length:        Resolution/ratio:        Source model and prompt:
--------------------------------------------------------------
LAYER A · generation realism
  Tier 1 defects: none / yes (label + timecode)
  Tier 2 defects: none / yes (label + timecode)
  Tier 3 defects: none / yes (label + timecode)
  Inside the focal area: yes / no
LAYER B · editing usability
  Motion: dead / directional (direction:      ) / clear head and tail
  Head quality:      Tail quality:
  Roles it can take: opening hook / establishing shot / subject close-up /
                     transition bridge / closing / ambient bed
--------------------------------------------------------------
Verdict: KEEP / KEEP-needs-fix (what:        ) / NG (reason label:        )
Paired with: shot number        for motion-to-motion or a match cut
```

---

## 3. The closed loop for AIGC editing

```
1. Write the shot plan first (shot no. / scale / camera move / action / sound / length budget)
         |
         v   Before generating, self-check the plan against the six dimensions.
             Can the order be reversed? Is the message clear?
2. Generate. Two to four candidates per shot, varying one prompt variable.
3. Run each clip through layer A (defects) and layer B (usability) -> KEEP / fix / NG
4. Assemble into sequences and run the six-dimension scorecard.
5. Fix, following the remedy order from cheapest to most expensive:
   cut point -> mask -> crop -> grade -> sound -> speed -> regenerate
6. Debrief: write the NG reason labels back into the prompt vocabulary.
   For tier 3, revise the prompt first:
     irreversibility or causality -> split into two shorter shots
     text -> keep text out of frame entirely
     synchronised multi-subject motion -> fewer subjects, or stagger the action
```

**The core discipline**: **coherence is not the same as knowing how to cut.** A model can produce a superficially coherent multi-shot video without having executed any editorial intent. Where the cuts fall, whether sound leads or lags, whether the transition logic holds: a person has to check each one.
