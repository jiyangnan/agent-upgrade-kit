#!/usr/bin/env python3
"""
Episodic Index Builder — Hybrid-Vector-Graph

Builds three index layers from memory/ markdown files:
1. Entity Graph: People, projects, tools, events → nodes + edges
2. Temporal Index: Time-ordered episode pointers
3. Tag Vectors: Co-occurrence based tag similarity

Usage:
  python3 build_index.py [--full] [--incremental]
  
  --full        Rebuild from scratch
  --incremental Only process files newer than last_rebuilt (default)
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

MEMORY_DIR = Path(os.path.expanduser("~/.openclaw/workspace/memory"))
INDEX_PATH = MEMORY_DIR / ".episodic_index.json"

# Entity patterns
ENTITY_PATTERNS = {
    "person": [
        r"@?(\b(?:白羊武士|Samantha|未晞|小南瓜|盖伦|小米粒|喵喵|Ferdinand)\b)",
        r"用户[：:]\s*(\w+)",
    ],
    "project": [
        r"(?:项目[：:]?\s*)?[\u300c\u3008\"']([\w\-]+(?:平台|系统|工具|课程|运营|监控|课程|kit))[\u300d\u3009\"']",
        r"(?:BotLearn|OpenClaw|Agent Reach|Rube MCP|Twitter自动化|虾评|agent-upgrade-kit|agent-cognitive-kit)",
    ],
    "tool": [
        r"(?:使用|用|安装了?)\s*[\u300c\u3008\"']?(\b(?:OpenClaw|Claude Code|Drizzle|Supabase|Next\.js|Playwright|faster-whisper|Obsidian|gh CLI|opencli|agent-reach|xreach|ChromaDB|Redis|PostgreSQL)\b)",
        r"\b([\w\-]+\.py)\b",
        r"\b(startup_hook|log_loop|build_index|query_index)\b",
    ],
    "event": [
        r"(\d{4}-\d{2}-\d{2})\s*(?:完成了?|发布了?|部署了?|修复了?|启动了?|发现了?)",
        r"(?:今日|今天|昨天)\s*(.+?)(?:\n|$)",
    ],
}

# Relation patterns
RELATION_KEYWORDS = {
    "worked_on": ["做了", "完成", "开发", "实现", "部署", "修复"],
    "uses": ["使用", "用", "采用", "安装"],
    "mentions": ["提到", "说了", "问"],
    "blocked_by": ["失败", "报错", "无法", "不行"],
    "resolved_by": ["解决了", "修复了", "搞定了"],
    "related_to": ["关联", "相关", "类似"],
}

TAG_PATTERN = re.compile(r"#(\w+)")
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


def extract_entities(text: str) -> list[dict]:
    """Extract entities from text."""
    entities = []
    seen = set()
    
    # Dynamic extraction: catch project names from headings and key-value pairs
    heading_pattern = re.compile(r'#{1,3}\s+(?:.+?[：:]\s*)?([\w\-]{3,}(?:kit|system|loop|hook|index|module))', re.IGNORECASE)
    for m in heading_pattern.finditer(text):
        name = m.group(1)
        if name not in seen and len(name) > 3:
            seen.add(name)
            entities.append({"name": name, "type": "project"})
    
    # Dynamic: catch backtick-wrapped names as tools
    tick_pattern = re.compile(r'`([\w\-]+\.(?:py|sh|js|md))`')
    for m in tick_pattern.finditer(text):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            entities.append({"name": name, "type": "tool"})
    
    for etype, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                name = match.group(0) if etype == "project" else match.group(1) if match.lastindex else match.group(0)
                key = (etype, name)
                if key not in seen:
                    seen.add(key)
                    entities.append({"type": etype, "name": name})
    return entities


def extract_relations(text: str, entities: list[dict]) -> list[dict]:
    """Extract relations between entities based on co-occurrence and keywords."""
    relations = []
    names = [e["name"] for e in entities]
    
    for rtype, keywords in RELATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                # Find pairs of entities in the same paragraph
                paragraphs = text.split("\n\n")
                for para in paragraphs:
                    if kw in para:
                        found = [n for n in names if n in para]
                        for i in range(len(found)):
                            for j in range(i + 1, len(found)):
                                relations.append({
                                    "source": found[i],
                                    "target": found[j],
                                    "type": rtype,
                                    "weight": 1,
                                })
    return relations


def extract_tags(text: str) -> list[str]:
    """Extract hashtags."""
    return list(set(TAG_PATTERN.findall(text)))


def extract_dates(text: str) -> list[str]:
    """Extract dates."""
    return list(set(DATE_PATTERN.findall(text)))


def build_index(mode="incremental"):
    """Build or update the episodic index."""
    
    # Load existing index
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            index = json.load(f)
    else:
        index = {
            "version": "1.0",
            "created": "2026-04-27",
            "entities": {},
            "relations": [],
            "temporal_index": {},
            "tag_vectors": {},
            "stats": {"total_episodes": 0, "total_entities": 0, "total_relations": 0, "last_rebuilt": ""},
        }
    
    if mode == "full":
        index["entities"] = {}
        index["relations"] = []
        index["temporal_index"] = {}
        index["tag_vectors"] = {}
    
    last_rebuilt = index["stats"].get("last_rebuilt", "")
    
    # Scan memory files
    md_files = sorted(MEMORY_DIR.glob("*.md"))
    processed = 0
    
    # Entity dedup tracking
    entity_occurrences = defaultdict(int)
    relation_map = defaultdict(int)  # (src, tgt, type) -> weight
    tag_cooccur = defaultdict(int)   # (tag1, tag2) -> count
    
    for md_file in md_files:
        # Skip if incremental and file older than last rebuild
        if mode == "incremental" and last_rebuilt:
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
            if mtime <= last_rebuilt:
                continue
        
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        if len(text) < 50:
            continue
        
        date = md_file.stem[:10]  # YYYY-MM-DD
        entities = extract_entities(text)
        relations = extract_relations(text, entities)
        tags = extract_tags(text)
        
        # Update entity index
        for e in entities:
            key = e["name"]
            if key not in index["entities"]:
                index["entities"][key] = {
                    "type": e["type"],
                    "first_seen": date,
                    "last_seen": date,
                    "occurrences": 0,
                    "episodes": [],
                    "tags": [],
                }
            index["entities"][key]["last_seen"] = date
            index["entities"][key]["occurrences"] += 1
            index["entities"][key]["episodes"].append(date)
            index["entities"][key]["tags"].extend(tags)
            entity_occurrences[key] += 1
        
        # Update relations (merge weights)
        for r in relations:
            rkey = (r["source"], r["target"], r["type"])
            relation_map[rkey] += r.get("weight", 1)
        
        # Update temporal index
        if date not in index["temporal_index"]:
            index["temporal_index"][date] = []
        index["temporal_index"][date].append({
            "file": md_file.name,
            "entities": [e["name"] for e in entities],
            "tags": tags,
        })
        
        # Update tag co-occurrence
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                pair = tuple(sorted([tags[i], tags[j]]))
                tag_cooccur[pair] += 1
        
        processed += 1
    
    # Merge relations
    existing_rels = {(r["source"], r["target"], r["type"]): r for r in index["relations"]}
    for (src, tgt, rtype), weight in relation_map.items():
        key = (src, tgt, rtype)
        if key in existing_rels:
            existing_rels[key]["weight"] += weight
        else:
            existing_rels[key] = {"source": src, "target": tgt, "type": rtype, "weight": weight}
    index["relations"] = list(existing_rels.values())
    
    # Build tag vectors (co-occurrence based)
    for (t1, t2), count in tag_cooccur.items():
        if t1 not in index["tag_vectors"]:
            index["tag_vectors"][t1] = {}
        if t2 not in index["tag_vectors"]:
            index["tag_vectors"][t2] = {}
        index["tag_vectors"][t1][t2] = count
        index["tag_vectors"][t2][t1] = count
    
    # Dedupe entity tags
    for key in index["entities"]:
        index["entities"][key]["tags"] = list(set(index["entities"][key]["tags"]))
    
    # Update stats
    index["stats"]["total_episodes"] = sum(len(v) for v in index["temporal_index"].values())
    index["stats"]["total_entities"] = len(index["entities"])
    index["stats"]["total_relations"] = len(index["relations"])
    index["stats"]["last_rebuilt"] = datetime.now().isoformat()
    
    # Write index
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Index built ({mode}): {processed} files processed")
    print(f"   Entities: {index['stats']['total_entities']}")
    print(f"   Relations: {index['stats']['total_relations']}")
    print(f"   Episodes: {index['stats']['total_episodes']}")
    print(f"   Tag clusters: {len(index['tag_vectors'])}")
    
    return index


if __name__ == "__main__":
    mode = "full" if "--full" in sys.argv else "incremental"
    build_index(mode)
