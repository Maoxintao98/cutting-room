# 落地执行 · DaVinci Resolve

判断做完之后，真正把片子剪出来。这条路走 DaVinci Resolve 21.1 自带的官方 MCP。

## 两种接入方式

**A. MCP 工具可用时（首选）**
Codex 把 `davinci_resolve` 挂成 MCP 工具后，直接调用即可。工具清单：

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
6 声音        NormalizeAudioLevel / AutoAlignClips
7 导出工程    EDL / FCPXML / DRT / OTIO
8 渲染        RenderSettings + StartRendering
9 自检        回看成品，走 review.md 的六维检查
```

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

**导出与渲染**

时间线导出类型是 `resolve.*` 常量，已验证存在的有：
`EXPORT_EDL`、`EXPORT_FCPXML_1_8`、`EXPORT_FCPXML_1_9`、`EXPORT_FCPXML_1_10`、`EXPORT_AAF`、`EXPORT_DRT`、`EXPORT_OTIO`、`EXPORT_ALE`。

渲染相关：`Project.StartRendering(jobIds)`、`Project.IsRenderingInProgress()`、`Project.GetRenderJobList()`，渲染设置里有 `ExportVideo`、`ExportAudio`、`ExportAlpha`、`ExportSubtitle`。

导出与渲染的具体方法名随版本变化，**动手前用 `search_scripting_api` 查一次**。

## 脚本骨架

```python
# cut.py，用 scripts/resolve_mcp.py run cut.py 执行
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
pool = project.GetMediaPool()

# 导入
items = pool.ImportMedia(["/path/to/素材目录"])

# 新建时间线并把素材铺上去
timeline = pool.CreateTimelineFromClips("cut_v1", [{"mediaPoolItem": i} for i in items])
project.SetCurrentTimeline(timeline)

print("时间线就绪:", timeline.GetName())
```

沙箱里的 `run_script` 只能碰 Resolve API。需要读脚本文件、写日志或调 ffmpeg 时改用 `run_script_unsafe`。

## 与 ffmpeg 的分工

Resolve 负责工程级的剪辑、调色、声音和交付。ffmpeg 负责它不擅长的部分：

- 素材盘点（`scripts/probe.py`）
- 抽帧看内容，生成 contact sheet
- 快速转码、生成代理、音频提取
- 渲染后的成品校验，例如核对时长、音轨、分辨率

两边配合的方式是先 ffmpeg 探明素材，再进 Resolve 做工程，最后用 ffmpeg 复核成品。
