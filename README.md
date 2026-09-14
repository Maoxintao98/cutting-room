# Cutting Room · 剪辑室

> 给编码 agent 用的**剪辑 skill**：剪片子、审片子、挑 AI 生成的素材。
> 它最不一样的地方不是"会剪"，而是**敢说实话**。

---

## 它解决什么问题

三个场景，对应三种用法：

| 用法 | 你现在的处境 | 它给你什么 |
|---|---|---|
| **评** | 片子剪完了，自己看花了眼；找人评又怕对方客气 | 六维评分 + **时间码证据** + 问题清单 + 能用／需修／重做的结论 |
| **剪** | 面对一堆素材，知道要剪，但不知道从哪下手、在哪切 | 先问清片种与目标，再按片种给出技法侧重 |
| **选** | AIGC 生成了几十条片段，挑到麻木 | 两级标签（生成瑕疵／剪辑可用性）+ KEEP／可修／NG 决策树 |

---

## 核心立场：八条底线

审片最大的敌人不是"看不出问题"，而是**不敢说**和**乱说**。所以这套规矩直接写进了主干：

**1. 不奉承，不软化**
禁用「整体不错，但是……」「瑕不掩瑜」「提点小建议」。
不因人情、关系、作者是谁而软化结论。**得罪人是这份工作的成本，不是失误。**

**2. 不凑数**
不为显得专业而编造问题——没问题就说没问题。
反过来同样：**不为格式对称而硬找优点**。强行平衡本身就是不诚实。

**3. 每条判断都要有证据**
指得出时间码／镜头号的才写。禁用语：震撼、高级、有质感、节奏不错——无证据的形容词只是噪音。

**4. 区分事实／共识／偏好**
把个人偏好伪装成标准，是审片最常见的失职。偏好必须标明【偏好】。

**5. 优点和缺点用同一把尺**
优点必须和缺点一样具体；**必须指出全片最好的那一个镜头，并说明为什么好**。
片子好就明确说好，不要用"但是"给它打折。

**6. 评价作品，不评价人**
但"不评人 ≠ 放水"。

**7. 说"不行"必须附上"为什么"和"怎么改"**
只否定不给路，等于没评。

**8. 不确定就说不确定**
缺什么信息（Brief／平台／硬性要求）直接讲，别编一个"听起来很专业"的结论。

---

## 它给的报告长什么样

（示例，内容为虚构）

```
片名/版本：demo-v1        片种：品牌氛围片      时长：25s      画幅：16:9
【信息缺口】未提供投放平台，可能影响对竖屏安全区的判断
────────────────────────────────────────────────
一、先说成立的
  1. 全片最好的镜头：第 12 秒，水滴落下时镜头向前推——
     运动方向与前一镜的旋转同向，是全片唯一一处真正接上的动势匹配剪
  2. 第 6 秒的 0.8 秒留白有动机：由动作触发，把注意力压回画面
  3. 色温全片统一；七次景别切换中六次保持了 ≥ 一档的变化

二、六维评分
  1 叙事推进            1/3   第 3 秒：该镜头与前后无因果关系，可删
  2 视听协同与声音设计  2/3   第 18 秒：音乐全程同一电平，高潮前无推进
  3 视觉构成与图文      1/3   第 9 秒：字幕压在人物面部
  4 镜头间连续性        2/3   第 7 秒：全景硬切特写，无过渡支点
  5 信息与品牌一致性    1/3   看完无法确定在卖什么
  6 时间节奏与速度      2/3   第 15 秒：变速方向与下一镜动势相反

三、问题清单（按"改动成本／收益比"排序）
  1.【高收益·低成本】第 18 秒 音乐缺推进 → 末段抬 4dB
  2.【高收益·低成本】第 3 秒 删掉该镜头 → 全片信息更清晰
  3.【高收益·高成本】第 5–9 秒 主体一致性有问题 → 需重新生成

四、结论
  ☐ 能用    ☑ 需修（改：音乐推进、第 3 秒删镜、第 5–9 秒重生成）
  一句话总评：单看每个镜头都成立，合起来不像同一支片子。
```

注意问题清单**按"改动成本／收益比"排序，不按严重程度**——一个 10 秒钟能改好的大问题，价值远高于一个要重拍的小问题。

---

## 为什么不是"让通用模型随便点评一下"

通用模型的影评有五个通病，这个 skill 把每一条都做成了禁令：

| 通病 | 对应禁令 |
|---|---|
| 上来先说"整体不错，但是……" | 底线 1 |
| 只讲观感，不指时间码 | 底线 3 |
| 把自己的口味当成标准 | 底线 4 |
| 只挑刺，看不见好的；或反过来硬夸 | 底线 2、5 |
| 指出问题却不给改法 | 底线 7 |

---

## 文件结构

```
SKILL.md               主干与路由（三种用法、八条底线、核心判断）
agents/openai.yaml     UI 元数据（显示名「剪辑室」）
references/
  craft.md             剪：术语表、六法则与六戒律、剪接点体系、节奏、声音、蒙太奇、转场、机位、拉片表
  review.md            评：客观性纪律、三遍看法流程、六维评分卡、审片报告模板、结论判定
  clip-qc.md           选：瑕疵三级／30 类分类、选片记录表、闭环工作法
```

按需加载：触发时只读 `SKILL.md`；审片不会去加载选片那份。

---

## 安装

Codex 会自动扫描以下位置，**放进去即生效，无需构建**：

```bash
# 用户级：对你所有项目生效
git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room

# 项目级：只对某个仓库生效
git clone https://github.com/Maoxintao98/cutting-room <你的仓库>/.agents/skills/cutting-room
```

调用方式：

- **显式**：`$cutting-room`
- **自然语言**：直接说人话（"审一下这条片子""哪些生成的镜头能用"），由 description 自动匹配

---

## English

A coding-agent skill for film editing, in three modes:

- **Cut** — where and why to cut, rhythm and sound design.
- **Review** — an honest, evidence-based critique of a finished cut: six-dimension scoring, issues with timecode evidence, and a ship / fix / rebuild verdict.
- **Select** — judging whether AI-generated clips are usable (KEEP / fix / NG), with a three-tier artifact taxonomy.

Its distinguishing feature is a stance, not a technique: **no flattery, no padding, every claim backed by a timecode** — plus the rule that strengths must be argued as concretely as weaknesses.

Install: `git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room`, then invoke with `$cutting-room`.

Primary language is Chinese; the trigger phrases in `description` are bilingual.

---

## 边界说明

- 内容蒸馏自剪辑经典著作与近期 AIGC 视频评估研究，**所有署名与出处已在 skill 内剥离**。
- 报告模板里的例子为虚构演示，不含任何真实客户或项目信息。

## License

MIT
