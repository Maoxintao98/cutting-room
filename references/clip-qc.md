# 单个生成片段 · 选片细则

> 判断**一个 AIGC 生成片段本身**能不能用。评价**整支成片**请看 [review.md](review.md)。

---

## 一、瑕疵分类学（三级 / 30 类）

按**"需要多深的推理才能发现"**分三级。命名与定义基于对大量 AIGC 视频失败模式的归纳，提炼出 30 个细粒度标签。

### 一级 · 表层瑕疵 Surface Artifacts
> 局部外观线索即可判断，看一眼就知道。

**色彩与曝光（Color & Exposure）**
- 色彩曝光异常 Color Exposure Anomaly——整体偏色、过曝/死黑、色彩漂移
- 光照阴影不一致 Lighting and Shadow Inconsistency——同一场景内光源方向/软硬矛盾
- 光照"烙进"画面 Baked-in Lighting——光效像贴图，不随物体运动变化

**摄影机与镜头（Camera & Lens）**
- 不自然的摄影机运动 Unnatural Camera Motion——抖动、突兀变速、无物理依据的运镜
- 光学失效 Optical Failure——失焦混乱、景深错误、焦外形状异常
- 折射失真 Refraction Distortion——透过玻璃/水/透明介质的折射不合物理
- 反射不一致 Reflection Inconsistency——镜面/水面倒影与实体不符，或反射不变形

**画质与纹理（Image Quality & Texture）**
- 模糊不一致 Inconsistent Blur——该清的地方糊、该糊的地方锐
- 纹理不一致 Texture Inconsistency——材质在帧间/区域间跳变
- 闪烁与噪点 Flickering and Noise
- 过度平滑 Oversmoothing——塑料感、磨皮感、细节被抹平

### 二级 · 结构性缺陷 Structural Defects
> 需要理解物体的组织方式才能发现。

**身份与形态（Identity & Morphology）**
- 不自然变形 Unnatural Morphing——刚体扭曲、物体像橡皮一样弯
- 多物体异常融合/分裂 Abnormal Multi-Object Merging/Splitting
- 特征不稳定 Feature Instability——同一对象的固有属性（发型、logo、纽扣数）在时序中突变
- 面部表情异常 Abnormal Facial Expression

**空间与纵深（Spatial & Depth）**
- 遮挡失效 Occlusion Failure——该被挡住的没被挡住
- 空间裁切 Spatial Clipping——物体穿模、切进别的物体里
- 纵深与透视失真 Depth & Perspective Distortion

**功能结构（Functional Structure）**
- 非生物结构缺失 Non-Biological Structural Loss——物体缺零件、结构断裂（车轮少一半、杯子缺把手）
- 生物解剖违例 Biological Anatomy Violation——六指、反关节、比例错乱

**光学一致性**：反射/折射与光照的跨帧一致性问题（与一级同族但需跨帧判断）。

### 三级 · 时序-语义违例 Temporal-Semantic Violations
> 需要跨帧整合 + 常识/因果推理。**最致命**——观众说不清，但会觉得"假"。

**动作（Unnatural Motion）**
- 不自然的生物运动 Unnatural Biological Motion——走路像飘、关节运动不对
- 多主体完全同步运动 Identical Multi-Subject Motion——一群人动作像克隆（"克隆人军团"）
- 动态与动力学不一致 Dynamic & Kinematic Inconsistency——速度/加速度/惯性违反物理

**因果（Causality）**
- 因果违例 Violation of Causality——A 不可能导致 B
- **不可逆性违例 Irreversibility Violation**——打碎的杯子复原、泼出的水收回（**最刺眼**）
- 有动作无后果 Action without Consequence——挥拳打在脸上，脸没反应
- 有后果无动作 Consequence without Valid Action——物体自己动了，没有触发动作

**常识（Commonsense）**
- 动作-语境错配 Action-Context Mismatch——在客厅里游泳
- 典型外观违例 Canonical Appearance Violation——香蕉是紫色的、消防车不是红的
- 常识失败 Commonsense Failure

**场景连贯（Scene Continuity）**
- 空间一致性 Spatial Coherence——主体相对位置/交互点前后矛盾
- 文字符号不可读 Text and Symbol Unreadable——招牌/字幕糊成鬼画符（**AI 成片的经典破绽**）
- 物体凭空出现/消失 Object Disappearance/Appearance
- 跨镜头一致性 Cross-Shot Coherence——切镜后服装/道具/发型/环境变了

### 严重度与处置对照
| 级别 | 典型处置 |
|---|---|
| 一级（表层） | 焦点区内：局部重生成；焦点区外：调色/降噪/缩短镜头 |
| 二级（结构） | 焦点区内：重生成；焦点区外：裁切重构图/遮挡/缩短 |
| 三级（时序-语义） | 多数须重生成；极端情况用"切掉+转场遮挡"绕过 |

**注**：分类学是**诊断性**而非互斥的。一个片段常同时命中多类（如"结构变形 + 时序不一致"），允许**多标签**。报告写多个标签比写一个更准确。

---

## 二、单片段选片记录表

```
文件名：
时长：        分辨率/比例：        来源模型与 prompt：
--------------------------------------------------------------
A 层 · 生成真实性
  一级瑕疵：无 / 有（标签 + 时间码）
  二级瑕疵：无 / 有（标签 + 时间码）
  三级瑕疵：无 / 有（标签 + 时间码）
  是否落在焦点区：是 / 否
B 层 · 剪辑可用性
  动势：死 / 有方向（方向：      ）/ 有明确起幅落幅
  入点质量：      出点质量：
  可直接承担的角色：开场钩子 / 建立镜头 / 主体特写 / 转场支点 / 收尾 / 氛围底
--------------------------------------------------------------
结论：KEEP / KEEP-需修（修什么：        ）/ NG（原因标签：        ）
可配对镜头：与        号可做动接动 / 匹配剪
```

---

## 三、AIGC 剪辑的闭环工作法

```
1. 先写 shot plan（分镜表：镜头号 / 景别 / 运镜 / 动作 / 声音 / 时长预算）
         ↓  ← 在生成之前，用六维自检计划：顺序能不能颠倒？信息清不清晰？
2. 生成 → 每段出 2–4 个候选（可变一个 prompt 变量）
3. 单片段过 A 层（瑕疵）+ B 层（可用性）→ KEEP / 可修 / NG
4. 组段 → 过六维评分卡
5. 修：按"补救手段优先级"从便宜到贵（切点→遮挡→裁切→调色→声音→变速→重生成）
6. 复盘：把 NG 的原因标签写回 prompt 词表（三级瑕疵优先改写提示词：
   不可逆性/因果类 → 拆分为两个更短的镜头；文字类 → 避免画面内文字；
   多主体同步 → 减少主体数量或明确先后动作）
```

**核心纪律**：**"连贯不等于会剪"**。模型能生成一段看起来连贯的多镜头视频，不代表它执行了剪辑意图——切点在哪、声音先入还是滞后、转场逻辑对不对，这些都要人逐条核对。
