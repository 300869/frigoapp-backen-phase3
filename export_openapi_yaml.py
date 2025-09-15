import json

import requests

try:
    import yaml  # pyyaml
except ImportError:
    yaml = None


def main():
    url = "http://127.0.0.1:8000/openapi.json"
    print(f"Fetching {url} ...")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    # Save JSON
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Save YAML (fallback to json->.yaml if pyyaml missing)
    if yaml:
        with open("freshkeeper-openapi.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        print("Wrote freshkeeper-openapi.yaml (via PyYAML)")
    else:
        with open("freshkeeper-openapi.yaml", "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        print(
            "PyYAML not found, wrote JSON text into .yaml (install with: pip install pyyaml)"
        )
    print("Done.")


if __name__ == "__main__":
    main()
