import os
import shutil
import stat
import time

SRC = "app"
DST = "freshkeeper"

os.makedirs(DST, exist_ok=True)
shutil.copytree(SRC, DST, dirs_exist_ok=True)


def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


for i in range(5):
    try:
        shutil.rmtree(SRC, onerror=on_rm_error)
        break
    except Exception as e:
        print(f"Retry remove {SRC} ({i+1}/5): {e}")
        time.sleep(1)

print("Done")
