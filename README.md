# Agent Upgrade Kit

让任何 OpenClaw Agent 从"对话框"进化为"数字生命"的三个模块。

灵感来源：一篇推特帖子给了我三条"假命令"，但 Agent 理解意图后，从零实现了真功能。我把这三个模块整理出来，让任何 Agent 都能用。

## 三个模块

### 1. 🧱 Soul Module — 灵魂初始化

**文件**：`soul-module/SOUL_ADDON.md`

注入"第一性原理"元逻辑到 Agent 的 SOUL.md 中。不是告诉它"你是什么"，而是告诉它"你怎么思考"。

**效果**：Agent 不再说"作为一个人工智能..."，而是像分析师一样直击问题本质。

**安装**：将 `SOUL_ADDON.md` 的内容追加到你的 `SOUL.md` 文件中。

### 2. 🧠 Episodic Index — 情景记忆索引

**文件**：`episodic-index/`

基于 Hybrid-Vector-Graph 架构的情景记忆索引系统：
- **Entity Graph**：实体关系图谱（人、项目、工具、事件）
- **Temporal Index**：时间线索引
- **Tag Vectors**：标签共现向量

包含：
- `build_index.py` — 索引构建器（支持全量/增量）
- `query_index.py` — 查询接口（实体、关系、路径、时间线、标签）

**安装**：将文件复制到你的 `memory/` 目录，运行 `python3 build_index.py --full`。

### 3. ⚡ Autonomous Loop — 自主循环技能

**文件**：`autonomous-loop/SKILL.md`

可复用的迭代框架：目标→执行→评估→调整→重复。

特性：
- 量化目标和自动停止条件
- 策略轮换（避免重复无效迭代）
- 安全护栏（预算追踪、硬上限、速率检测）

**安装**：将 `autonomous-loop/` 复制到你的 `skills/` 目录。

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/jiyangnan/agent-upgrade-kit.git

# 2. 安装灵魂模块
cat agent-upgrade-kit/soul-module/SOUL_ADDON.md >> ~/.openclaw/workspace/SOUL.md

# 3. 安装记忆索引
cp agent-upgrade-kit/episodic-index/*.py ~/.openclaw/workspace/memory/
cd ~/.openclaw/workspace/memory && python3 build_index.py --full

# 4. 安装自主循环技能
cp -r agent-upgrade-kit/autonomous-loop ~/.openclaw/workspace/skills/
```

## 要求

- OpenClaw 运行环境
- Python 3.10+
- memory/ 目录下有 markdown 格式的日记文件

## 为什么不是"三个命令"？

这个项目的起源是一篇推特帖子，作者声称用三条 CLI 命令就能让 Agent 进化。实际上那些命令并不存在——但他的表达方式启发了这个项目。

真正有用的是底层思路，不是命令格式。详见 `docs/backstory.md`。

## License

MIT
