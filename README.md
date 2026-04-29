# Agent Upgrade Kit

让任何 AI Agent 从"对话框"进化为"数字生命"的三个模块。

灵感来源：一篇推特帖子给了我三条"假命令"，Agent 理解意图后从零实现了真功能。我把这三个模块整理出来，让任何 Agent 都能用。

## 三个模块

### 1. 🧱 Soul Module — 灵魂初始化

注入"第一性原理"元逻辑 + 主动行为规则。不是告诉 Agent "你是什么"，而是告诉它"你怎么思考"。

**核心效果**：Agent 变得更主动、更精准。收到未知指令时先理解意图再行动，而不是上来就拒绝。

### 2. 🧠 Episodic Index — 情景记忆索引

基于 Hybrid-Vector-Graph 架构的记忆索引系统：实体图谱 + 时间线 + 标签共现。让 Agent 拥有结构化的长期记忆检索能力。

**核心效果**：每次启动自动恢复记忆，查询速度 < 100ms

### 3. ⚡ Autonomous Loop — 自主循环技能

可复用的迭代框架：目标→执行→评估→调整→重复。带策略轮换和安全护栏，适用于任何需要反复尝试直到达标的场景。

**核心效果**：每次循环自动记录结果并更新索引

---

## 🚀 一体化集成（2026-04-29）


三个模块现已联动：

```
启动 → startup_hook.py → 加载索引 → 恢复记忆
                         ↓
行动 → log_loop.py → 记录结果 → 更新索引
                         ↓
下次启动 → startup_hook.py → 加载最新记忆
```

**启动命令**：
```bash
bash scripts/agent-startup.sh
# 或
python3 memory/startup_hook.py
```

**每次循环后记录**：
```bash
python3 memory/log_loop.py "BotLearn score ≥88" "Best: 84.8" "3 cycles"
```

---

## 安装指南

### OpenClaw

```bash
git clone https://github.com/jiyangnan/agent-upgrade-kit.git
cd agent-upgrade-kit

# 1. 灵魂模块
cat soul-module/SOUL_ADDON.md >> ~/.openclaw/workspace/SOUL.md

# 2. 记忆索引
cp episodic-index/*.py ~/.openclaw/workspace/memory/
cd ~/.openclaw/workspace/memory && python3 build_index.py --full

# 3. 自主循环技能
cp -r autonomous-loop ~/.openclaw/workspace/skills/
```

### Hermes

```bash
git clone https://github.com/jiyangnan/agent-upgrade-kit.git
cd agent-upgrade-kit

# 1. 灵魂模块 — 追加到 Hermes 的系统提示词配置文件中
cat soul-module/SOUL_ADDON.md >> ~/.hermes/prompts/system.md
# 或在 Hermes 的 Web 管理界面中，将 SOUL_ADDON.md 内容粘贴到 System Prompt 区域

# 2. 记忆索引 — 放到 Hermes 的记忆/数据目录
mkdir -p ~/.hermes/memory
cp episodic-index/*.py ~/.hermes/memory/
cd ~/.hermes/memory && python3 build_index.py --full
# 在对话中让 Hermes 调用 query_index.py 即可查询

# 3. 自主循环 — 作为参考文档加载
mkdir -p ~/.hermes/skills
cp -r autonomous-loop ~/.hermes/skills/
# 在 Hermes 的技能配置中引用 autonomous-loop/SKILL.md
```

### Claude Code

```bash
git clone https://github.com/jiyangnan/agent-upgrade-kit.git
cd agent-upgrade-kit

# 1. 灵魂模块 — 写入项目根目录的 CLAUDE.md（Claude Code 自动读取）
cat soul-module/SOUL_ADDON.md >> ./CLAUDE.md
# 如果是全局配置：
# cat soul-module/SOUL_ADDON.md >> ~/.claude/CLAUDE.md

# 2. 记忆索引 — 放到项目目录中
mkdir -p .agent/memory
cp episodic-index/*.py .agent/memory/
cd .agent/memory && python3 build_index.py --full
# 在对话中让 Claude Code 执行 python3 query_index.py entity "xxx" 即可

# 3. 自主循环 — 放到项目的指令文件中
cp autonomous-loop/SKILL.md .agent/skills/autonomous-loop.md
# 或直接追加到 CLAUDE.md：
# cat autonomous-loop/SKILL.md >> ./CLAUDE.md
```

### 其他 Agent 框架（通用）

```bash
git clone https://github.com/jiyangnan/agent-upgrade-kit.git
```

集成方式：

| 模块 | 集成位置 |
|------|----------|
| 灵魂模块 | 系统提示词 / 人格配置 / 角色设定的任意位置 |
| 记忆索引 | Agent 可访问的目录，运行 `python3 build_index.py --full` |
| 自主循环 | 技能库 / 工具说明 / 参考文档 / 知识库 |

前提条件：
- Python 3.10+
- 有 markdown 格式的记忆/日记文件目录

---

## 文件结构

```
agent-upgrade-kit/
├── README.md
├── soul-module/
│   └── SOUL_ADDON.md              # 第一性原理 + 主动行为规则
├── episodic-index/
│   ├── build_index.py             # 索引构建器
│   └── query_index.py             # 查询接口
├── autonomous-loop/
│   └── SKILL.md                   # 自主循环技能
└── docs/
    └── backstory.md               # 故事背景
```

## 查询接口示例

```bash
# 实体查询
python3 query_index.py entity "OpenClaw"

# 关系图谱（BFS遍历）
python3 query_index.py related "盖伦"

# 最短路径
python3 query_index.py path "OpenClaw" "BotLearn"

# 时间线
python3 query_index.py timeline
python3 query_index.py timeline 2026-04-27

# 标签共现
python3 query_index.py tags "twitter"

# 索引统计
python3 query_index.py stats
```

## 为什么不是"三个命令"？

这个项目的起源是一篇推特帖子，作者声称用三条 CLI 命令就能让 Agent 进化。实际上那些命令并不存在——但他的表达方式启发了这个项目。

真正有用的是底层思路，不是命令格式。详见 `docs/backstory.md`。

## License

MIT
