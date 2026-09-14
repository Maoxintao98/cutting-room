# Cutting Room

**A coding-agent skill for film editing.** It cuts, it reviews, and it judges whether AI-generated clips are usable.

Ask a model to critique an edit and you usually get something like *"The pacing is strong, though the second act could be tighter."* Polite, unfalsifiable, useless. This skill exists to prevent that.

---

## Three modes

| Mode | Your situation | What you get |
|---|---|---|
| **Review** | The cut is done, you have stared at it too long, and asking a colleague feels awkward | Scores on six dimensions, every issue pinned to a timecode, and a verdict of ship, fix, or rebuild |
| **Cut** | You have the footage and no idea where to begin | An intake that settles the film's type and goal first, then the technique priorities for that type |
| **Select** | Forty generated clips and no way to choose | Two independent labels (generation defects / editing usability) and a keep / fix / discard decision tree |

## The eight rules

Reviewing is hard for two reasons. One is not daring to say the thing. The other is saying it carelessly. The rules below exist to prevent both.

1. **No flattery, no softening.** Openers like "overall it's solid, but..." are banned. The verdict does not change because of who made the film. Calling something a rebuild job is part of the work, not a breach of manners.
2. **No padding.** Never invent a problem to look thorough. If nothing is wrong, say so. The reverse holds too, so do not manufacture praise for symmetry. Forced balance is its own kind of dishonesty.
3. **Every claim carries evidence.** If you cannot point at a timecode or a shot number, do not write it. Words like *stunning* and *great energy* add nothing.
4. **Separate fact, consensus, and taste.** A personal preference has to be marked as one. Passing taste off as a standard is the most common failure in review work.
5. **Hold strengths and weaknesses to the same bar.** A strength must be as specific as a critique, and the review must name the single best shot in the film and explain why it works. If the film is good, say so plainly, with no "but" hanging off it.
6. **Criticise the work, not the maker.** That is not the same as going easy on it.
7. **"This doesn't work" arrives with a why and a suggestion.** A rejection with no path forward is not a review.
8. **Say when you don't know.** Missing the brief, the target platform, or a hard client requirement? Name the gap instead of inventing a confident-sounding verdict.

## What a review looks like

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

3. Issues, ordered by cost/benefit rather than severity
   1. [High benefit, low cost]  00:18 lift the final music section by 4dB
   2. [High benefit, low cost]  00:03 cut the shot, the film reads clearer
   3. [High benefit, high cost] 00:05-09 subject consistency needs a regen

4. Verdict
   [ ] ship    [x] fix (music build, cut at 00:03, regen 00:05-09)
   In one line. Every shot works alone. Together, they do not feel like
   one film.
```

Issues are ordered by **cost against benefit, not severity**. A large problem that takes ten seconds to fix is worth more attention than a small one that needs a reshoot.

## Where it comes from

A distillation of **24 books, 19 research papers, and 27 articles**, roughly 12 million characters of extracted text.

The books run the length of the editing tradition, from montage through realism. The papers cover 2023 to 2026 work on evaluating generated video. The skill folds all of it into one method and carries no citations in its own text.

## Install

Codex scans these locations automatically. Cloning is the whole install.

```bash
# User level, applies to every project
git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room

# Project level, applies to one repository
git clone https://github.com/Maoxintao98/cutting-room <your-repo>/.agents/skills/cutting-room
```

Invoke it as `$cutting-room`, or just describe the task ("review this cut") and the description handles matching.

## Contents

```
SKILL.md               Main body and routing
agents/openai.yaml     UI metadata
references/
  craft.md             Cutting: terminology, priorities, cut points, rhythm, sound, montage, transitions, blocking
  review.md            Reviewing: the discipline, a three-pass method, the six-dimension rubric, report template
  clip-qc.md           Selecting: a three-tier defect taxonomy, per-clip record sheet
```

Only `SKILL.md` loads on trigger. Reviewing will not pull in the clip-selection reference.

---

## 中文

给编码 agent 用的剪辑 skill，能做三件事。剪片子、审片子，挑 AI 生成的素材。

| 用法 | 场景 | 产出 |
|---|---|---|
| **评** | 片子剪完了，自己看花了眼，找人评又怕对方客气 | 六维评分、时间码证据、问题清单，以及能用／需修／重做的结论 |
| **剪** | 素材在手，不知道从哪下手 | 先问清片种与目标，再给这个片种的技法侧重 |
| **选** | AIGC 生成了几十条片段，挑到麻木 | 生成瑕疵与剪辑可用性两级标签，以及 KEEP／可修／NG 决策树 |

审片难在两处，一是不敢说，二是乱说。八条规矩防的就是这两件事。

不奉承，不软化。不因为片子是谁做的，就改口径。不为了显得专业而编造问题，也不为了格式对称硬找优点。每条判断都要指得出时间码。个人口味必须标明是口味。优点和缺点用同一把尺，还得指出全片最好的那个镜头，说明它好在哪。说"不行"的时候，要给出为什么和怎么改。

缺 Brief、缺平台、缺硬性要求，就直接讲。别编。

底本是一个 24 本书、19 篇论文、27 篇文章的资料库，抽取全文约一千二百万字符，覆盖从蒙太奇到写实主义的剪辑主线，以及近三年评估生成视频的研究。skill 把这些整理成一套统一方法，正文不带引用。

安装和调用方式见英文部分。

## License

MIT
