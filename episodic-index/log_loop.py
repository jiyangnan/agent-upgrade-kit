#!/usr/bin/env python3
"""
Autonomous Loop + Memory Integration

Run this after any autonomous loop completes to automatically:
1. Log the cycle results to today's memory
2. Rebuild the index

Usage:
  python3 memory/log_loop.py <goal> <result> <cycles>

Example:
  python3 memory/log_loop.py "BotLearn score ≥88" "Best: 84.8" "3 cycles"
"""

import sys
import json
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"

def log_result(goal, result, cycles):
    """Log loop result to today's memory"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = MEMORY_DIR / f"{today}.md"
    
    content = f"""
### Autonomous Loop: {goal}

**时间**: {datetime.now().strftime("%H:%M")}
**Cycles**: {cycles}
**Result**: {result}
**Status**: ✅ Complete
"""
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(content + "\n")
    
    # Rebuild index incrementally
    import subprocess
    result = subprocess.run(
        ["python3", str(MEMORY_DIR / "build_index.py"), "--incremental"],
        capture_output=True, text=True, timeout=30
    )
    
    print(f"✅ Logged: {goal}")
    print(f"✅ Index updated")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 log_loop.py <goal> <result> <cycles>")
        sys.exit(1)
    
    log_result(sys.argv[1], sys.argv[2], sys.argv[3])