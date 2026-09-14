# 落地执行 · DaVinci Resolve

判断做完之后，把时间线剪出来。这条路走 DaVinci Resolve 21.1 自带的官方 MCP。

**交付物是一条编辑好的时间线，不是渲染好的文件。**渲染由用户自己跑。

## 两种接入方式

**A. MCP 工具可用时（首选）**
Codex 把 `davinci_resolve` 挂成 MCP 工具后，直接调用即可。可用工具如下。

| 工具 | 用途 |
|---|---|
| `run_script` | 沙箱 Python，可访问 DaVinciResolveScript API |
| `run_script_unsafe` | 同上，另带文件系统、网络、子进程权限 |
| `search_scripting_api` | 按关键词搜 API 的类型与函数 |
| `get_scripting_api` | 拉取指定类型的完整声明 |
| `get_scripting_docs` | 开发者文档 |
| `get_resolve_status` / `launch_resolve` | 查状态、启动 Resolve |
| `update_dctl` / `generate_lut` / `list_luts` 等 | LUT 与 DCTL 管理 |

**B. MCP 工具没挂上时（保底）**
用 `scripts/resolve_mcp.py` 直连同一个服务器，能力完全一致。

```bash
python3 scripts/resolve_mcp.py status              # Resolve 在跑吗
python3 scripts/resolve_mcp.py search Timeline     # 查 API
python3 scripts/resolve_mcp.py run cut.py          # 执行脚本
```

## 工具契约（写脚本前必读）

`run_script` 和 `run_script_unsafe` 有几条硬规定，写错任何一条都会得到一个
"script completed with no output or result"，而且不报错。

| 规定 | 说明 |
|---|---|
| 参数名是 `script` | 不是 `code`。写错参数名不会报错，只会静默无输出 |
| 预注入变量 | `resolve` 和 `project` 直接可用，不需要自己取 |
| 返回数据 | 把结构化结果赋给 `result` 变量。`print()` 的输出也会被捕获 |
| 超时 | 默认 10 秒，**上限 60 秒**。长任务要拆成多步 |
| 沙箱限制 | `run_script` 屏蔽 `os`、`sys`、`pathlib`、`shutil` |

需要文件系统或子进程时用 `run_script_unsafe`，其余情况一律用 `run_script`。

**步骤脚本配套三个脚本**，都在 `scripts/` 下。

```bash
python3 scripts/resolve_mcp.py status          # Resolve 在跑吗
python3 scripts/run_step.py steps/10_picture.py            # 沙箱执行
python3 scripts/run_step.py steps/30_titles.py --unsafe    # 放开文件系统
python3 scripts/run_step.py steps/30_titles.py --pre lib/titles.py lib/common.py
```

`run_step.py` 的 `--pre` 解决沙箱不能 import 的问题，把共享代码拼进脚本文本再投递。

步骤脚本的写法是每步只做一件事，并以 `result` 返回。

```python
result = {"project": project.GetName()}
tl = project.GetCurrentTimeline()
if tl:
    result["timeline"] = tl.GetName()
    result["end_frame"] = tl.GetEndFrame()
```

## 三条铁律

**一、先查再写。** 动手前用 `search_scripting_api` 确认函数签名，不要凭记忆写 API。脚本 API 随版本变动，背下来的很容易过期。查一次只要几秒，写错了要重跑。

**二、不覆盖用户的工程。** 开工前另存为新项目或新时间线，原有工程保持不动。用户的工程里可能有他手动的调色和剪辑。

**三、大改动先报方案。** 删片段、改结构、批量操作、起渲染之前，先把要做什么讲清楚再动手。这些小改动的成本远低于做错。

## 执行流水线

```
1 盘点素材    scripts/probe.py <素材目录>
2 建工程      打开或新建项目，设定时间线分辨率与帧率
3 导入素材    MediaPool.ImportMedia
4 建时间线    MediaPool.CreateTimelineFromClips / Timeline.AddTrack
5 剪辑        AppendToTimeline / DeleteClips / SetClipsLinked
6 覆盖层      字幕、图形走 Fusion comp，单独一遍处理
7 声音        NormalizeAudioLevel / AutoAlignClips
8 体检        scripts/steps/00_inspect_timeline.py
9 交接        报告时间线状态，渲染交给用户
```

## 时间线自检

**交给用户之前跑一遍体检。**这个脚本用区间合并算覆盖，只把真正没被任何片段盖住的地方算作空隙，转场压着片段不会误报。

```bash
python3 scripts/run_step.py scripts/steps/00_inspect_timeline.py
```

输出包含帧率、时长、每轨的片段数与转场数、空隙位置。判断规则有两条。

**主画面轨（video 1）必须连续**，有空隙就是问题。覆写轨、字幕轨、音效轨允许有空隙，那只是没铺满，不算错。

**超出时间线末尾是真问题**，任何轨道都要报。

顺带会提示空的视频轨，可以删掉。

## 已核实的 API（21.1）

**取对象**

```python
resolve  = dvr_script.scriptapp("Resolve")
project  = resolve.GetProjectManager().GetCurrentProject()
pool     = project.GetMediaPool()
timeline = project.GetCurrentTimeline()
```

**素材与时间线**

| 调用 | 作用 |
|---|---|
| `MediaPool.ImportMedia(clipInfos)` | 导入文件或文件夹到当前媒体夹 |
| `MediaPool.CreateTimelineFromClips(name, clipInfos)` | 用素材新建时间线 |
| `MediaPool.AppendToTimeline(clipInfos)` | 往当前时间线追加片段 |
| `Timeline.AddTrack(trackType, subTrackType)` | 加轨道 |
| `Timeline.DeleteClips(items, rippleDelete)` | 删片段，可选波纹删除 |
| `Timeline.SetClipsLinked(items, linked)` | 链接或断开音视频 |
| `Project.SetCurrentTimeline(timeline)` | 切换当前时间线 |
| `Project.GetTimelineByIndex(idx)` | 按序号取时间线 |

**声音**

| 调用 | 作用 |
|---|---|
| `Timeline.NormalizeAudioLevel(items, options)` | 音量归一 |
| `Timeline.AutoAlignClips(items, options)` | 自动对齐 |

**导出与渲染**（渲染由用户负责，这里只作备查）

时间线导出类型是 `resolve.*` 常量。已验证存在的有 `EXPORT_EDL`、`EXPORT_FCPXML_1_8`、`EXPORT_FCPXML_1_9`、`EXPORT_FCPXML_1_10`、`EXPORT_AAF`、`EXPORT_DRT`、`EXPORT_OTIO`、`EXPORT_ALE`。

渲染相关的有 `Project.StartRendering(jobIds)`、`Project.IsRenderingInProgress()`、`Project.GetRenderJobList()`，渲染设置里有 `ExportVideo`、`ExportAudio`、`ExportAlpha`、`ExportSubtitle`。

导出与渲染的具体方法名随版本变化，**动手前用 `search_scripting_api` 查一次**。

## 脚本骨架

沙箱里 `resolve` 和 `project` 已经注入好了，不要再自己取，也不要 import。

```python
# steps/10_picture.py
# 用 python3 scripts/run_step.py steps/10_picture.py 执行
result = {}

pool = project.GetMediaPool()
items = pool.ImportMedia(["/path/to/素材目录"])
result["imported"] = len(items)

timeline = pool.CreateTimelineFromClips(
    "cut_v1", [{"mediaPoolItem": i} for i in items]
)
project.SetCurrentTimeline(timeline)
result["timeline"] = timeline.GetName()
result["end_frame"] = timeline.GetEndFrame()
```

约定三条。只做一件事，用 `result` 返回，失败时不抛异常而是把错误写进 `result`。

需要读脚本文件、写日志或调 ffmpeg 时用 `run_script_unsafe`，并把步骤脚本里要用的共享代码用 `--pre` 拼进来。

## 与 ffmpeg 的分工

Resolve 负责工程级的剪辑、调色、声音和交付。ffmpeg 负责它不擅长的部分。

- 素材盘点（`scripts/probe.py`）
- 抽帧看内容，生成 contact sheet
- 快速转码、生成代理、音频提取
- 渲染后的成品校验，例如核对时长、音轨、分辨率

两边配合的方式是先 ffmpeg 探明素材，再进 Resolve 做工程，最后用 ffmpeg 复核成品。

## 实战坑位

以下每一条都是实际驱动 Resolve 时踩出来的，会直接决定脚本写法和排查顺序。

**一、沙箱没有文件系统。**
`run_script` 里不能读文件，也不能 import 本地模块。需要读写文件或调子进程时改用 `run_script_unsafe`。共享代码没法 import，只能在调用之前把源码拼进脚本再执行。

**二、追加片段和挂 Fusion comp 要分两次调用。**
`AppendToTimeline` 当场返回的对象挂不上 Fusion comp，同一个脚本里接着做会全部返回 None。正确做法是先跑一遍只做追加，再跑一遍取回片段、挂 comp。

**三、Fusion 找不到字体会让渲染直接崩。**
报错形如 `Font Not Found: PingFang SC Bold`。Fusion 会默认去取 Bold，系统里未必有。设置 `Font` 之前先查字体表。

```python
fusion = resolve.Fusion()
fonts = fusion.FontManager.GetFontList()   # FontManager 是属性，不是方法
names = list(fonts.keys())                 # 取其中确实存在的字体名再用
```

写成 `fusion.FontManager()` 会拿到 None，然后报一个和字体无关的错误。

**四、渲染会中途失败而不明确报错。**
`StartRendering` 返回 True 只表示任务已提交。必须轮询 `GetRenderJobStatus` 看 `JobStatus`，并留意 `CompletionPercentage` 停在哪。渲染完成后再用 ffprobe 核对帧数，实际帧数明显少于时长乘帧率就是没渲染完。

**五、`ExportCurrentFrameAsStill` 不可靠。**
可能反复返回 None，Resolve 是否在前台、停在哪个页面都会影响它。要做抽帧检查时用 ffmpeg 更稳。

**六、多个会话会抢同一个 Resolve。**
同时有别的会话在驱动同一个 Resolve 时，脚本通道互相打断，症状是大面积返回 None 和各种异常。动手前确认只有一个会话在驱动。

**七、每步都打印 JSON。**
把工作拆成编号的步骤脚本，每步只做一件事，结束时输出结构化结果。Resolve 的脚本通道不稳定，一次做太多，失败时无从定位。排查用的 `probe`、`diag`、`try` 步骤会写得很多，这是正常的。
