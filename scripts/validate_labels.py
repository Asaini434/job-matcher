from pathlib import Path

from pydantic import ValidationError

from jobmatcher.models import Label

failures = 0

for path in sorted(Path("data/labels").glob("*.json")):
    try:
        Label.model_validate_json(path.read_text())
        print(f"OK    {path.stem}")
    except ValidationError as e:
        failures += 1
        print(f"FAIL  {path.stem}")
        print(e)

print(f"\n{failures} file(s) failed")