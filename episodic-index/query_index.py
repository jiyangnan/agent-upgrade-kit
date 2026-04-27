#!/usr/bin/env python3
"""
Episodic Index Query Tool

Usage:
  python3 query_index.py entity <name>           # Look up entity and its relations
  python3 query_index.py related <name>           # Find all connected entities (graph traversal)
  python3 query_index.py timeline [YYYY-MM-DD]    # Show timeline or specific date
  python3 query_index.py tags <tag>               # Find related tags and episodes
  python3 query_index.py path <entity1> <entity2> # Find shortest path between entities
  python3 query_index.py stats                    # Index statistics
"""

import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path

INDEX_PATH = Path(os.path.expanduser("~/.openclaw/workspace/memory/.episodic_index.json"))


def load_index():
    with open(INDEX_PATH) as f:
        return json.load(f)


def cmd_entity(idx, name):
    """Look up entity details."""
    if name in idx["entities"]:
        e = idx["entities"][name]
        print(f"📌 {name} ({e['type']})")
        print(f"   First seen: {e['first_seen']}")
        print(f"   Last seen:  {e['last_seen']}")
        print(f"   Occurrences: {e['occurrences']}")
        print(f"   Tags: {', '.join('#' + t for t in e['tags'][:10])}")
        print(f"   Episodes: {', '.join(e['episodes'][:10])}")
    else:
        # Fuzzy match
        matches = [k for k in idx["entities"] if name.lower() in k.lower()]
        if matches:
            print(f"Exact match not found. Similar: {', '.join(matches[:5])}")
        else:
            print(f"Entity '{name}' not found")

    # Show relations
    rels = [r for r in idx["relations"] if r["source"] == name or r["target"] == name]
    if rels:
        print(f"\n🔗 Relations ({len(rels)}):")
        for r in sorted(rels, key=lambda x: x["weight"], reverse=True)[:10]:
            other = r["target"] if r["source"] == name else r["source"]
            direction = "→" if r["source"] == name else "←"
            print(f"   {name} {direction}[{r['type']}] {other} (w={r['weight']})")


def cmd_related(idx, name, depth=2):
    """Graph traversal — find all entities connected to name."""
    if name not in idx["entities"]:
        print(f"Entity '{name}' not found")
        return

    visited = {name}
    frontier = deque([(name, 0)])
    result = defaultdict(list)

    while frontier:
        current, d = frontier.popleft()
        if d >= depth:
            continue
        for r in idx["relations"]:
            if r["source"] == current and r["target"] not in visited:
                visited.add(r["target"])
                frontier.append((r["target"], d + 1))
                result[d + 1].append((r["target"], r["type"], r["weight"]))
            elif r["target"] == current and r["source"] not in visited:
                visited.add(r["source"])
                frontier.append((r["source"], d + 1))
                result[d + 1].append((r["source"], r["type"], r["weight"]))

    print(f"🌐 Entities related to '{name}' (depth={depth}):")
    for d in sorted(result.keys()):
        items = sorted(result[d], key=lambda x: x[2], reverse=True)
        print(f"\n  Depth {d}:")
        for entity, rtype, weight in items[:8]:
            etype = idx["entities"].get(entity, {}).get("type", "?")
            print(f"    {entity} ({etype}) via [{rtype}] w={weight}")


def cmd_timeline(idx, date=None):
    """Show timeline."""
    if date:
        if date in idx["temporal_index"]:
            episodes = idx["temporal_index"][date]
            print(f"📅 {date} — {len(episodes)} episode(s)")
            for ep in episodes:
                print(f"  📄 {ep['file']}")
                print(f"     Entities: {', '.join(ep['entities'][:8])}")
                print(f"     Tags: {', '.join('#' + t for t in ep['tags'][:8])}")
        else:
            print(f"No episodes found for {date}")
    else:
        dates = sorted(idx["temporal_index"].keys(), reverse=True)[:15]
        print(f"📅 Recent timeline ({len(dates)} of {len(idx['temporal_index'])} dates):")
        for d in dates:
            eps = idx["temporal_index"][d]
            entities = set()
            for ep in eps:
                entities.update(ep["entities"])
            print(f"  {d}: {len(eps)} episodes | {', '.join(list(entities)[:6])}")


def cmd_tags(idx, tag):
    """Find related tags and episodes."""
    tag = tag.lstrip("#")
    if tag in idx["tag_vectors"]:
        related = sorted(idx["tag_vectors"][tag].items(), key=lambda x: x[1], reverse=True)
        print(f"🏷️ #{tag} — related tags:")
        for t, count in related[:10]:
            print(f"  #{t} (co-occurrence: {count})")
    else:
        print(f"Tag #{tag} not found")
        similar = [t for t in idx["tag_vectors"] if tag in t]
        if similar:
            print(f"Similar: {', '.join('#' + t for t in similar[:5])}")

    # Find episodes with this tag
    episodes = []
    for date, eps in idx["temporal_index"].items():
        for ep in eps:
            if tag in ep["tags"]:
                episodes.append((date, ep))
    if episodes:
        print(f"\n📅 Episodes with #{tag} ({len(episodes)}):")
        for date, ep in sorted(episodes, reverse=True)[:10]:
            print(f"  {date}: {ep['file']}")


def cmd_path(idx, source, target):
    """Find shortest path between entities using BFS."""
    if source not in idx["entities"] or target not in idx["entities"]:
        print(f"Entity not found: {source if source not in idx['entities'] else target}")
        return

    # Build adjacency list
    adj = defaultdict(list)
    for r in idx["relations"]:
        adj[r["source"]].append((r["target"], r["type"], r["weight"]))
        adj[r["target"]].append((r["source"], r["type"], r["weight"]))

    # BFS
    visited = {source}
    queue = deque([(source, [(source, None, 0)])])

    while queue:
        current, path = queue.popleft()
        if current == target:
            print(f"🛤️ Path: {source} → {target}")
            total_weight = 0
            for node, rtype, weight in path[1:]:
                print(f"  --[{rtype}]--> {node} (w={weight})")
                total_weight += weight
            print(f"  Total weight: {total_weight}")
            return

        for neighbor, rtype, weight in adj[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [(neighbor, rtype, weight)]))

    print(f"No path found between {source} and {target}")


def cmd_stats(idx):
    """Show index statistics."""
    print("📊 Episodic Index Stats")
    print(f"   Version: {idx['version']}")
    print(f"   Last rebuilt: {idx['stats']['last_rebuilt']}")
    print(f"   Episodes: {idx['stats']['total_episodes']}")
    print(f"   Entities: {idx['stats']['total_entities']}")
    print(f"   Relations: {idx['stats']['total_relations']}")
    print(f"   Tag clusters: {len(idx['tag_vectors'])}")

    # Entity type breakdown
    types = defaultdict(int)
    for e in idx["entities"].values():
        types[e["type"]] += 1
    print(f"\n   Entity types: {dict(types)}")


if __name__ == "__main__":
    import os
    idx = load_index()
    
    if len(sys.argv) < 2:
        cmd_stats(idx)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "entity":
        cmd_entity(idx, sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "related":
        cmd_related(idx, sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "timeline":
        cmd_timeline(idx, sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "tags":
        cmd_tags(idx, sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "path":
        if len(sys.argv) >= 4:
            cmd_path(idx, sys.argv[2], sys.argv[3])
        else:
            print("Usage: query_index.py path <source> <target>")
    elif cmd == "stats":
        cmd_stats(idx)
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: entity, related, timeline, tags, path, stats")
