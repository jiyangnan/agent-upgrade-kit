# Agent Upgrade Kit

让任何 AI Agent 从"对话框"进化为"数字生命"的三个模块。

灵感来源：一篇推特帖子给了我三条"假命令"，Agent 理解意图后从零实现了真功能。我把这三个模块整理出来，让任何 Agent 都能用——不限于 OpenClaw。

## 三个模块

### 1. 🧱 Soul Module — 灵魂初始化

**文件**：`soul-module/SOUL_ADDON.md`

注入"第一性原理"元逻辑到 Agent 的人设/系统提示词中。不是告诉它"你是什么"，而是告诉它"你怎么思考"。

同时包含一条关键行为规则：**收到未知指令时，先理解意图，再决定是否拒绝**——而不是上来就说"这不是标准功能"。

**效果**：Agent 变得更主动、更精准，不再说"作为一个人工智能..."。

**安装方式**（通用）：
- 将 `SOUL_ADDON.md` 的内容追加到你的 Agent 的系统提示词、SOUL.md、人格配置文件中
- 或作为 system prompt 的一部分注入

**安装方式**（OpenClaw）：
```bash
cat soul-module/SOUL_ADDON.md >> ~/.openclaw/workspace/SOUL.md
```

### 2. 🧠 Episodic Index — 情景记忆索引

**文件**：`episodic-index/`

基于 Hybrid-Vector-Graph 架构的情景记忆索引系统：
- **Entity Graph**：实体关系图谱（人、项目、工具、事件）
- **Temporal Index**：时间线索引
- **Tag Vectors**：标签共现向量

包含：
- `build_index.py` — 索引构建器（支持全量/增量）
- `query_index.py` — 查询接口（实体查询、关系图谱、最短路径、时间线、标签共现）

**前提**：需要有一个存放 markdown 格式记忆/日记文件的目录。

**安装方式**（通用）：
```bash
# 将文件复制到你的记忆目录
cp episodic-index/*.py /your/memory/directory/
cd /your/memory/directory
python3 build_index.py --full

# 查询
python3 query_index.py entity "某个实体名"
python3 query_index.py path "实体A" "实体B"
python3 query_index.py timeline
python3 query_index.py tags "某个标签"
```

**安装方式**（OpenClaw）：
```bash
cp episodic-index/*.py ~/.openclaw/workspace/memory/
cd ~/.openclaw/workspace/memory && python3 build_index.py --full
```

### 3. ⚡ Autonomous Loop — 自主循环技能

**文件**：`autonomous-loop/SKILL.md`

可复用的迭代框架：目标→执行→评估→调整→重复。

特性：
- 量化目标和自动停止条件
- 策略轮换（避免重复无效迭代）
- 安全护栏（预算追踪、硬上限、速率检测）
- 适用于任何需要反复尝试直到达标的场景（考试冲分、代码优化、方案迭代等）

**安装方式**（通用）：
- 将 `SKILL.md` 的内容作为技能/工具说明加载到你的 Agent 中
- 或直接把内容粘贴到 Agent 可访问的知识库/参考文档中
- 当用户说"继续冲"、"迭代直到"、"keep going"等触发词时，Agent 应读取此文件

**安装方式**（OpenClaw）：
```bash
cp -r autonomous-loop ~/.openclaw/workspace/skills/
```

## 通用安装（任何 Agent）

```bash
git clone https://github.com/jiyangnan/agent-upgrade-kit.git
```

然后根据你使用的 Agent 框架，按上述各模块的说明集成：

1. **灵魂模块** → 追加到系统提示词/人格配置
2. **记忆索引** → 放到记忆目录，运行构建脚本
3. **自主循环** → 加到技能库或参考文档

## 为什么不是"三个命令"？

这个项目的起源是一篇推特帖子，作者声称用三条 CLI 命令就能让 Agent 进化。实际上那些命令并不存在——但他的表达方式启发了这个项目。

真正有用的是底层思路，不是命令格式。详见 `docs/backstory.md`。

## License

MIT
