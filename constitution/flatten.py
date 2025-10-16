import requests
import os
import json

# 1. Download canonical core CLD from Witchborn repo
CLD_URL = "https://raw.githubusercontent.com/dimentox/aci/main/core_cld.json"
core_cld = requests.get(CLD_URL).json()

# 2. Load local amendments in order (from ./amendments directory)
amendment_dir = "./amendments"
amendments = []
if os.path.isdir(amendment_dir):
    for fname in sorted(os.listdir(amendment_dir)):
        if fname.endswith(".json"):
            with open(os.path.join(amendment_dir, fname), encoding="utf-8") as f:
                try:
                    amendments.append(json.load(f))
                except Exception as e:
                    print(f"Failed to load amendment {fname}: {e}")

# 3. Merge core law and amendments into a single list
flattened_law = core_cld + amendments

# 4. Write a Markdown file for system prompt injection (LLM prompt, audit, etc)
def flatten_law_md(laws):
    return "### Flattened Constitution\n\n" + "\n".join([f"{l['id']}: {l['article']}" for l in laws])

with open("compiled_constitution.md", "w", encoding="utf-8") as f:
    f.write(flatten_law_md(flattened_law))

print("Flattened CLD compiled and saved to compiled_constitution.md.")
