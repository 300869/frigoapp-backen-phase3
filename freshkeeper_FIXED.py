#!/usr/bin/env python3
"""
bulk_rename_to_freshkeeper.py

USAGE:
  python bulk_rename_to_freshkeeper.py <project_root>

What it does safely:
  - Backs up files it modifies into .backup_rename/
  - Replaces package names 'frigoapp' and 'FrigoApp' -> 'freshkeeper' / 'FreshKeeper'
  - Rewrites imports 'from freshkeeper' / 'import freshkeeper' -> 'from freshkeeper' / 'import freshkeeper'
  - Renames folders: frigoapp-backen-phase3 -> freshkeeper-backend-phase3
                     frigoapp -> freshkeeper
                     app -> freshkeeper (only if it's a Python package, i.e., has __init__.py)
  - Skips venv/.git/__pycache__ etc.
"""
import os
import re
import shutil
import sys
from typing import List, Tuple

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}
TEXT_EXT = {
    ".py",
    ".env",
    ".ini",
    ".cfg",
    ".toml",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
}

Patterns = List[Tuple[str, str]]


def replace_in_file(path: str, patterns: Patterns) -> bool:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    new = content
    for pat, repl in patterns:
        new = re.sub(pat, repl, content)
    if new != content:
        # backup
        bdir = os.path.join(os.path.dirname(path), ".backup_rename")
        os.makedirs(bdir, exist_ok=True)
        shutil.copy2(path, os.path.join(bdir, os.path.basename(path)))
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        return True
    return False


def main(root: str) -> None:
    if not os.path.isdir(root):
        print(f"[error] Project root not found: {root}")
        sys.exit(2)

    # 1) Textual replacements (order matters a bit)
    patterns: Patterns = [
        (r"\bfrigoapp\b", "freshkeeper"),
        (r"\bFrigoApp\b", "FreshKeeper"),
        (r"\bFRIGOAPP\b", "FRESHKEEPER"),
        # imports 'app' -> 'freshkeeper' only in proper contexts
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

    # 2) Folder renames (process bottom-up)
    rename_pairs = []
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        for d in dirnames:
            src = os.path.join(dirpath, d)
            if d == "frigoapp-backen-phase3":
                rename_pairs.append(
                    (src, os.path.join(dirpath, "freshkeeper-backend-phase3"))
                )
            elif d == "frigoapp":
                rename_pairs.append((src, os.path.join(dirpath, "freshkeeper")))
            elif d == "app":
                # only rename if it's a Python package (has __init__.py)
                pkg = os.path.join(src, "__init__.py")
                if os.path.exists(pkg):
                    rename_pairs.append((src, os.path.join(dirpath, "freshkeeper")))

    for src, dst in rename_pairs:
        if os.path.exists(src) and not os.path.exists(dst):
            print(f"[rename] {src} -> {dst}")
            os.rename(src, dst)

    print("Done. Verify imports and run tests.")
    print(
        "If Alembic package path changed, update env.py target_metadata import to freshkeeper.models.Base (or your path)."
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        print("Usage: python bulk_rename_to_freshkeeper.py <project_root>")
        sys.exit(1)
    main(sys.argv[1])
