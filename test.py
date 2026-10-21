import json
from category import get_category

for video in get_category("/search/family"):
    print(json.dumps(video, indent=2, ensure_ascii=False), flush=True)