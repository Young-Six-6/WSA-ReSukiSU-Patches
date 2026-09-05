#!/usr/bin/env python3
"""Prepare the pinned SUSFS module for WSA.

The x64 variant replaces the upstream ARM64-only helper with a native x86_64
build and prevents module actions from downloading an ARM64 replacement.
Both variants disable the animated WebUI background that crashes some WSA AMD
graphics stacks and expose only the SUSFS 2.x auto-hide controls that work.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


GPU_COMPAT = """
\t<!-- wsa-webui-gpu-compat: avoid the animated canvas/backdrop path that can
\t     crash WsaClient in the host AMD OpenGL driver. -->
\t<style id="wsa-webui-gpu-compat">
\t\t#backgroundCanvas { display: none !important; }
\t\t* {
\t\t\t-webkit-backdrop-filter: none !important;
\t\t\tbackdrop-filter: none !important;
\t\t}
\t</style>
\t<script>
\t\t(() => {
\t\t\tconst originalGetContext = HTMLCanvasElement.prototype.getContext;
\t\t\tconst noop = () => {};
\t\t\tconst backgroundContext = {
\t\t\t\tclearRect: noop, beginPath: noop, arc: noop, fill: noop,
\t\t\t\tdrawImage: noop, save: noop, translate: noop, rotate: noop,
\t\t\t\trestore: noop, set fillStyle(value) {}
\t\t\t};
\t\t\tHTMLCanvasElement.prototype.getContext = function(type, ...args) {
\t\t\t\tif (this.id === "backgroundCanvas" && type === "2d")
\t\t\t\t\treturn backgroundContext;
\t\t\t\treturn originalGetContext.call(this, type, ...args);
\t\t\t};
\t\t})();
\t</script>
""".strip("\n")


X64_ACTION = """#!/system/bin/sh
MODDIR=${0%/*}
SOURCE_BIN="$MODDIR/tools/ksu_susfs_arm64"
DEST_BIN=/data/adb/ksu/bin/ksu_susfs

echo "[-] Restoring the bundled WSA x86_64 ksu_susfs helper"
if [ ! -x "$SOURCE_BIN" ]; then
    echo "[!] Bundled helper is missing"
    exit 1
fi
cp -f "$SOURCE_BIN" "$DEST_BIN" || exit 1
chmod 0755 "$DEST_BIN" || exit 1
"$DEST_BIN" show version || exit 1
echo "[-] Native WSA helper installed"
"""


X64_BIN_CHECK = """#!/system/bin/sh
MODDIR=${0%/*}
SOURCE_BIN="$MODDIR/tools/ksu_susfs_arm64"
DEST_BIN=/data/adb/ksu/bin/ksu_susfs

if [ -x "$SOURCE_BIN" ] && [ -x "$DEST_BIN" ] && cmp -s "$SOURCE_BIN" "$DEST_BIN"; then
    echo match
else
    echo mismatch
fi
"""


X64_BIN_UPDATE = """#!/system/bin/sh
MODDIR=${0%/*}
SOURCE_BIN="$MODDIR/tools/ksu_susfs_arm64"
DEST_BIN=/data/adb/ksu/bin/ksu_susfs

cp -f "$SOURCE_BIN" "$DEST_BIN" || exit 1
chmod 0755 "$DEST_BIN" || exit 1
"$DEST_BIN" show version
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one {label} marker, found {count}")
    return text.replace(old, new, 1)


def patch_webui(module_dir: Path) -> None:
    index = module_dir / "webroot" / "index.html"
    html = index.read_text(encoding="utf-8")
    if "wsa-webui-gpu-compat" not in html:
        anchor = '  <script type="module"'
        if anchor not in html:
            raise RuntimeError("WebUI module script marker is missing")
        html = html.replace(anchor, GPU_COMPAT + "\n" + anchor, 1)
        index.write_text(html, encoding="utf-8", newline="\n")

    candidates = []
    for path in (module_dir / "webroot" / "assets").glob("index-*.js"):
        data = path.read_text(encoding="utf-8")
        if "async function W(" in data and "auto_try_umount_toggle" in data:
            candidates.append((path, data))
    if len(candidates) != 1:
        raise RuntimeError(f"expected one main WebUI bundle, found {len(candidates)}")

    js_path, js = candidates[0]
    # R28 reports module version 1.5.2 although this WebUI gates these controls
    # at 1.5.4/1.5.5/1.5.7. SUSFS 2.3.0 was tested with the userspace umount
    # control and the non-su mount-hide supercall, so expose those two only.
    js = replace_once(js, "v(E,1,5,4)&&W(", "W(", "auto-hide initializer")
    js = replace_once(js, "v(n,1,5,7)?(", "!0?(", "non-su mount-hide gate")
    js = replace_once(
        js,
        'v(n,1,5,5)&&L.classList.remove("hidden")',
        'L.classList.remove("hidden")',
        "userspace auto-umount gate",
    )
    js_path.write_text(js, encoding="utf-8", newline="\n")


def prepare_x64(module_dir: Path, native_tool: Path) -> None:
    if not native_tool.is_file():
        raise FileNotFoundError(native_tool)

    tools = module_dir / "tools"
    bundled = tools / "ksu_susfs_arm64"
    explicit = tools / "ksu_susfs_x86_64"
    shutil.copy2(native_tool, bundled)
    shutil.copy2(native_tool, explicit)
    os.chmod(bundled, 0o755)
    os.chmod(explicit, 0o755)

    customize = module_dir / "customize.sh"
    text = customize.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'if check "$base_url"; then',
        'if false; then # WSA x86_64: never replace the native helper with ARM64',
        "customize binary download gate",
    )
    customize.write_text(text, encoding="utf-8", newline="\n")

    (module_dir / "action.sh").write_text(X64_ACTION, encoding="utf-8", newline="\n")
    (module_dir / "susfs-bin-check.sh").write_text(
        X64_BIN_CHECK, encoding="utf-8", newline="\n"
    )
    (module_dir / "susfs-bin-update.sh").write_text(
        X64_BIN_UPDATE, encoding="utf-8", newline="\n"
    )
    for name in ("action.sh", "susfs-bin-check.sh", "susfs-bin-update.sh"):
        os.chmod(module_dir / name, 0o755)


def update_metadata(module_dir: Path, arch: str) -> None:
    prop = module_dir / "module.prop"
    text = prop.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "name=SUSFS-FOR-KERNELSU",
        f"name=SUSFS-FOR-KERNELSU (WSA {arch})",
        "module name",
    )
    text = replace_once(
        text,
        "description=An addon root hiding service for KernelSU compiled with patched kernel source.",
        "description=WSA-compatible SUSFS module with native helper and GPU-safe WebUI.",
        "module description",
    )
    if arch == "x64":
        # An upstream module update would reinstall its ARM64-only helper.
        text = "\n".join(
            line for line in text.splitlines() if not line.startswith("updateJson=")
        ) + "\n"
    prop.write_text(text, encoding="utf-8", newline="\n")

    notes = module_dir / "WSA-COMPATIBILITY.txt"
    notes.write_text(
        "WSA compatibility changes:\n"
        "- GPU-safe WebUI (animated canvas and backdrop blur disabled).\n"
        "- SUSFS 2.x userspace auto-umount and non-su mount-hide controls exposed.\n"
        + (
            "- Native x86_64 ksu_susfs helper; ARM64 online replacement disabled.\n"
            if arch == "x64"
            else "- Upstream ARM64 ksu_susfs helper retained.\n"
        ),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module-dir", required=True, type=Path)
    parser.add_argument("--arch", required=True, choices=("x64", "arm64"))
    parser.add_argument("--native-tool", type=Path)
    args = parser.parse_args()

    module_dir = args.module_dir.resolve()
    if args.arch == "x64":
        if args.native_tool is None:
            parser.error("--native-tool is required for x64")
        prepare_x64(module_dir, args.native_tool.resolve())
    patch_webui(module_dir)
    update_metadata(module_dir, args.arch)
    print(f"Prepared WSA SUSFS module for {args.arch}: {module_dir}")


if __name__ == "__main__":
    main()
