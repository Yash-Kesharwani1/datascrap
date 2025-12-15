import json
from jsonschema import validate, ValidationError

with open("./data/job_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

jsonl_file = "./data/jobs.jsonl"

valid_count = 0
invalid_count = 0

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):

        if not line.strip():
            continue  # skip empty lines

        try:
            data = json.loads(line)
            validate(instance=data, schema=schema)
            valid_count += 1

        except json.JSONDecodeError as e:
            invalid_count += 1
            print(f"\n❌ JSON decode error at line {line_number}")
            print(e)

        except ValidationError as e:
            invalid_count += 1

            # Build readable JSON path
            error_path = " -> ".join([str(p) for p in e.path]) or "ROOT"

            print(f"\n❌ Schema mismatch at line {line_number}")
            print(f"📍 Path     : {error_path}")
            print(f"⚠️  Reason   : {e.message}")
            print(f"📘 Expected : {e.schema}")

print("\n========== SUMMARY ==========")
print("✅ Valid records:", valid_count)
print("❌ Invalid records:", invalid_count)