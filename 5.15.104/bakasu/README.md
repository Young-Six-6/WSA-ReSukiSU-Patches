# BakaSU compatibility patches

These patches target the pinned BakaSU commit documented in the repository README and are applied after the WSA kernel hook patches.

- The shared compatibility patch supports both /system/bin/su and /product/bin/su, keeps authorized su requests available to no-su-marked WSA processes, redirects lookup-only probes, falls back to /system/bin/sh if ksud is missing, rewrites argv[0], and defers SELinux initialization when init's second-stage hook is missed.
- The GET_INFO patch preserves the legacy version/flags prefix ABI for callers that provide no size field.

The SUSFS build uses this same BakaSU patch set. SUSFS-specific changes to the WSA kernel tree are kept in the sibling susfs directory.
