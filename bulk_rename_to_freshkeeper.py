
import os
import re
import shutil
import sys

USAGE:
  python bulk_rename_to_freshkeeper.py <project_root>

What it does safely:
  - Backs up files it modifies into .backup_rename/
  - Replaces package names 'frigoapp' and bare 'app' -> 'freshkeeper' in .py/.env/.toml/.ini/.yml/.yaml
  - Renames top-level folders and references:
      frigoapp-backen-phase3 -> freshkeeper-backend-phase3
      frigoapp, app (package dirs) -> freshkeeper
  - Skips venv, .git, __pycache__

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}
TEXT_EXT = {".py", ".env", ".ini", ".cfg", ".toml", ".md", ".txt", ".yml", ".yaml", ".json"}

def replace_in_file(path, patterns):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    new = content
    for pat, repl in patterns:
        new = re.sub(pat, repl, new)
    if new != content:
        # backup
        bdir = os.path.join(os.path.dirname(path), ".backup_rename")
        os.makedirs(bdir, exist_ok=True)
        shutil.copy2(path, os.path.join(bdir, os.path.basename(path)))
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        return True
    return False

def main(root):
    # 1) textual replacements
    patterns = [
        (r"\bfrigoapp\b", "freshkeeper"),
        (r"\bFrigoApp\b", "FreshKeeper"),
        (r"\bFRIGOAPP\b", "FRESHKEEPER"),
        # optional: replace bare package 'app' only in imports "from freshkeeper" or "import freshkeeper"
        (r"\bfrom\s+app\b", "from freshkeeper"),
        (r"\bimport\s+app\b", "import freshkeeper"),
    ]
    changed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXT:
                p = os.path.join(dirpath, fn)
                if replace_in_file(p, patterns):
                    changed += 1
    print(f"[rename] Updated {changed} files")

    # 2) folder renames (order matters: rename deeper first)
    rename_pairs = []
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        for d in dirnames:
            if d == "frigoapp-backen-phase3":
                rename_pairs.append((os.path.join(dirpath, d), os.path.join(dirpath, "freshkeeper-backend-phase3")))
            elif d == "frigoapp":
                rename_pairs.append((os.path.join(dirpath, d), os.path.join(dirpath, "freshkeeper")))
            elif d == "app":
                # only rename if it's a Python package (has __init__.py)
                pkg = os.path.join(dirpath, d, "__init__.py")
                if os.path.exists(pkg):
                    rename_pairs.append((os.path.join(dirpath, d), os.path.join(dirpath, "freshkeeper")))

    for src, dst in rename_pairs:
        if os.path.exists(src) and not os.path.exists(dst):
            print(f"[rename] {src} -> {dst}")
            os.rename(src, dst)

    print("Done. Verify imports and run tests.")
    print("If Alembic package path changed, update env.py target_metadata import to freshkeeper.models.Base")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print("Usage: python bulk_rename_to_freshkeeper.py <project_root>")
        sys.exit(1)
    main(sys.argv[1])

