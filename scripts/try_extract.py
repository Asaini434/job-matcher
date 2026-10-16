import sys
from pathlib import Path

from jobmatcher.extract import extract_requirements

posting_id = sys.argv[1]
text = Path(f"data/postings/{posting_id}.txt").read_text()

result = extract_requirements(text)
print(result.model_dump_json(indent=2))