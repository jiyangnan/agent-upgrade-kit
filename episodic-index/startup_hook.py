#!/usr/bin/env python3
"""
Startup Hook - Integrates all three modules for Agent memory
Run this on every agent startup/initialization
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"
INDEX_PATH = MEMORY_DIR / ".episodic_index.json"

def load_last_state():
    """从向量索引恢复上次状态"""
    print("\n" + "="*50)
    print("🚀 Loading agent memory...")
    print("="*50)
    
    try:
        # 1. 查询索引统计
        result = subprocess.run(
            ["python3", str(MEMORY_DIR / "query_index.py"), "stats"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            print(result.stdout)
        
        # 2. 查询最近的时间线
        result = subprocess.run(
            ["python3", str(MEMORY_DIR / "query_index.py"), "timeline"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[:10]
            print("\n📅 Recent timeline:")
            for line in lines:
                print(f"  {line}")
                
    except Exception as e:
        print(f"⚠️ Index query failed: {e}")
    
    print("="*50)
    print("✅ Memory system loaded")
    print("="*50 + "\n")

def ensure_index_built():
    """确保索引已构建"""
    # 检查索引文件是否存在
    if not INDEX_PATH.exists():
        print("🔨 Building index from scratch...")
        result = subprocess.run(
            ["python3", str(MEMORY_DIR / "build_index.py"), "--full"],
            capture_output=True, text=True, timeout=120
        )
        print(result.stdout)
        return
    
    # 检查索引是否过期（超过24小时）
    try:
        with open(INDEX_PATH) as f:
            index = json.load(f)
        last_built = index.get("stats", {}).get("last_rebuilt", "")
        if last_built:
            last_time = datetime.fromisoformat(last_built.replace('Z', '+00:00'))
            if datetime.now() - last_time > timedelta(hours=24):
                print("🔨 Index is stale (>24h), rebuilding...")
                result = subprocess.run(
                    ["python3", str(MEMORY_DIR / "build_index.py"), "--full"],
                    capture_output=True, text=True, timeout=120
                )
                print(result.stdout)
    except Exception as e:
        print(f"⚠️ Index check failed: {e}")

def log_startup():
    """记录本次启动"""
    try:
        with open(MEMORY_DIR / ".conversation_state.json") as f:
            state = json.load(f)
        
        state["lastActivity"] = int(datetime.now().timestamp())
        state["agent_version"] = "v2.0-autonomous"
        
        with open(MEMORY_DIR / ".conversation_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass

if __name__ == "__main__":
    # 检查索引
    ensure_index_built()
    
    # 恢复状态
    load_last_state()
    
    # 记录启动
    log_startup()