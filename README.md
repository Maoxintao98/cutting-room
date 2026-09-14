# Cutting Room · 剪辑室

给编码 agent 用的**剪辑 skill**：剪片子、审片子、挑 AI 生成的素材。

三种用法共用一套判断：

| 用法 | 什么时候用 |
|---|---|
| **剪** | 决定在哪切、为什么切、搭节奏与声音设计 |
| **评** | 对一条**成片**给出客观、有证据、不掺人情的评审（六维评分 + 问题清单 + 能用／需修／重做） |
| **选** | 判断 **AIGC 生成片段**能不能用（KEEP／NG）并排序 |

## 它的立场

审片部分立了**八条底线**，前两条是核心：

1. **不奉承，不软化** —— 禁用语：「整体不错，但是……」「瑕不掩瑜」。不因人情、作者是谁而软化结论。**得罪人是这份工作的成本，不是失误。**
2. **不凑数** —— 不为显得专业而编造问题；**也不为格式对称而硬找优点**。强行平衡本身就是不诚实。

其余：每条判断都要有证据（指得出时间码）；区分**客观事实／专业共识／个人偏好**并标明；优点和缺点用同一把尺；说"不行"必须附上"为什么"和"怎么改"。

## 内容

```
SKILL.md                  主干与路由
references/craft.md       剪：术语、六法则、剪接点体系、节奏、声音、蒙太奇、转场、机位、拉片表
references/review.md      评：客观性纪律、三遍看法、六维评分卡、审片报告模板
references/clip-qc.md     选：瑕疵三级分类、选片记录表
agents/openai.yaml        UI 元数据
```

## 安装

Codex 会自动扫描这些位置，放进去即生效（无需构建）：

```bash
# 用户级：对你所有项目生效
git clone https://github.com/Maoxintao98/cutting-room ~/.agents/skills/cutting-room

# 项目级：只对某个仓库生效
git clone https://github.com/Maoxintao98/cutting-room <你的仓库>/.agents/skills/cutting-room
```

调用：`$cutting-room`，或直接说人话（"审一下这条片子"）由 description 自动匹配。

## License

MIT
