# -*- coding: utf-8 -*-
"""wages_master.json에 2022년 노임단가 블록 추가 (참고치, 공식 단가로 교체 권장)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "wages_master.json"

with open(PATH, "r", encoding="utf-8") as f:
    d = json.load(f)

# 2022: 2023 대비 약 3% 하락 참고치
d["2022"] = {
    "기술사": {"govt_daily": 412000, "md_basic": 214017},
    "특급기술자": {"govt_daily": 313000, "md_basic": 162651},
    "고급기술자": {"govt_daily": 285000, "md_basic": 148050},
    "중급기술자": {"govt_daily": 240000, "md_basic": 124680},
    "초급기술자": {"govt_daily": 211000, "md_basic": 109622},
    "고급숙련기술자": {"govt_daily": 228000, "md_basic": 118428},
    "중급숙련기술자": {"govt_daily": 203000, "md_basic": 105559},
    "초급숙련기술자": {"govt_daily": 178000, "md_basic": 92494},
    "단순노무종사원": {"govt_daily": 82100, "md_basic": 82100},
}

keys = sorted(d.keys(), key=int)
out = {k: d[k] for k in keys}
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("2022 added. Years:", list(out.keys()))
