# WSA SUSFS compatibility layer

These patches are applied after the pinned upstream SUSFS Android 13 / Linux
5.15 kernel patch. They reproduce the source used by the tested WSA x86_64
kernel.

- Keep virtual `/system/bin/su` and `/product/bin/su` reachable for authorized
  applications after SUSFS marks their process as `no_su`.
- Restore `argv[0]` to `su` before handing execution to `ksud`.
- Retain the WSA lookup-only virtual-su redirect when SUSFS is enabled.
- Adapt the upstream fanotify callback to the WSA 5.15 ABI.
- Use `vm_end` because this WSA tree has no `VMA_PAD_START` helper.

Upstream SUSFS source is pinned by the workflow; the upstream KernelSU patch is
not applied because the pinned ReSukiSU revision already contains that
integration.
