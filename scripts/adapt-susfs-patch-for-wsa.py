#!/usr/bin/env python3
"""Drop Android trace-hook include hunks absent from the pinned WSA 5.15 tree.

The matching SUSFS definitions are added by the checked-in WSA context patch.
All other hunks remain byte-for-byte from the pinned upstream patch.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HUNKS = (
    (
        "fs/namespace.c",
        "@@ -32,11 +32,21 @@",
        ("trace/hooks/blk.h", "CL_COPY_MNT_NS BIT(25)", "susfs_is_current_ksu_domain"),
    ),
    (
        "fs/proc/task_mmu.c",
        "@@ -22,6 +22,9 @@",
        ("trace/hooks/mm.h", "linux/susfs_def.h", "CONFIG_KSU_SUSFS_SUS_MAP"),
    ),
)


def remove_hunk(text: str, path: str, header: str, markers: tuple[str, ...]) -> str:
    section_header = f"diff --git a/{path} b/{path}"
    if text.count(section_header) != 1:
        raise ValueError(f"expected one upstream patch section for {path}")

    section_start = text.index(section_header)
    next_section = text.find("\ndiff --git ", section_start + len(section_header))
    if next_section < 0:
        next_section = len(text)
    else:
        next_section += 1

    section = text[section_start:next_section]
    lines = section.splitlines(keepends=True)
    hunk_indices = [i for i, line in enumerate(lines) if line.startswith("@@ ")]
    starts = [i for i in hunk_indices if lines[i].startswith(header)]
    if len(starts) != 1:
        raise ValueError(f"expected one {header} hunk in {path}")

    start = starts[0]
    end = next((i for i in hunk_indices if i > start), len(lines))
    removed = "".join(lines[start:end])
    for marker in markers:
        if marker not in removed:
            raise ValueError(f"expected marker {marker!r} in {path} hunk")

    adapted_section = "".join(lines[:start] + lines[end:])
    return text[:section_start] + adapted_section + text[next_section:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("upstream_patch", type=Path)
    parser.add_argument("output_patch", type=Path)
    args = parser.parse_args()

    patch_text = args.upstream_patch.read_text(encoding="utf-8")
    for path, header, markers in HUNKS:
        patch_text = remove_hunk(patch_text, path, header, markers)

    args.output_patch.parent.mkdir(parents=True, exist_ok=True)
    args.output_patch.write_text(patch_text, encoding="utf-8", newline="\n")
    print(f"Created WSA-adapted SUSFS patch: {args.output_patch}")


if __name__ == "__main__":
    main()
