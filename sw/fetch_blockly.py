"""Download the Blockly library files used by the mLabScope Blockly tab.

Run once from the sw/ folder:   venv\\Scripts\\python fetch_blockly.py

Fetches blockly@11.2.2 from the npm registry and copies the files below into
support/blockly/ (next to blockly.html and mlab_blocks.js, which are ours).
"""

import io
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

VERSION = "11.2.2"
URL = f"https://registry.npmjs.org/blockly/-/blockly-{VERSION}.tgz"
DEST = Path(__file__).resolve().parent / "support" / "blockly"

FILES = [
    "blockly_compressed.js",
    "blocks_compressed.js",
    "python_compressed.js",
    "msg/en.js",
]
MEDIA_PREFIX = "media/"


def main() -> int:
    print(f"Downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=60) as resp:
        data = resp.read()

    copied = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.startswith("package/"):
                continue
            rel = member.name[len("package/"):]
            if rel not in FILES and not rel.startswith(MEDIA_PREFIX):
                continue
            target = DEST / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
            copied += 1

    missing = [f for f in FILES if not (DEST / f).exists()]
    if missing:
        print(f"ERROR: missing after download: {missing}")
        return 1
    (DEST / "BLOCKLY_VERSION.txt").write_text(
        f"Blockly {VERSION} (https://github.com/google/blockly), Apache License 2.0.\n"
        f"Files copied unmodified from the npm package blockly@{VERSION}.\n"
    )
    print(f"OK: {copied} files copied to {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
