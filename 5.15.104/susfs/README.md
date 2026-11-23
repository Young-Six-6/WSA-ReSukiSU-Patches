# WSA SUSFS compatibility patches

Applied after the pinned SUSFS Android 13 / Linux 5.15 patch and the BakaSU compatibility patch.

- Rebase two upstream include hunks that expect Android trace-hook headers absent from WSA; the adapter preserves the upstream patch body and supplies the equivalent SUSFS declarations for the WSA tree.
- Keep authorized virtual su path lookups working with the SUSFS no-su process flag.
- Preserve the WSA no-su exception in the SUSFS exec path.
- Adapt the upstream fanotify callback to the WSA 5.15 ABI.
- Use vm_end because the WSA tree has no VMA_PAD_START helper.

The sucompat path matcher, public path-check helpers, alternate /product/bin/su path, and argv[0] rewrite live in the shared BakaSU patch. This directory contains only kernel-tree changes required by the SUSFS variant.
