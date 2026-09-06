# WSA-ReSukiSU-Patches

## 项目简介

本项目为 WSA 5.15.104 提供 ReSukiSU 所需的手动钩子补丁，并提供 GitHub
Actions 工作流自动构建可替换的 WSA 内核。项目同时维护一个可选的 SUSFS
版本，用于在 WSA Android 容器中提供 root 隐藏和相关兼容功能。

## 构建方式

在 Actions 页面手动运行 `Build 5.15.104 with ReSukiSU`，可选择：

- `Target architecture`：选择 `x64` 或 `arm64`。
- `Also build and publish the SUSFS variant`：关闭时只构建普通 ReSukiSU
  内核；开启时同时构建普通版和 SUSFS 版，并在同一个运行结果中上传两套产物。
- `Create one GitHub Release...`：是否将本次选中的全部产物创建为 Release。

工作流会在上传前验证内核配置、SUSFS 源码版本、模块文件、工具架构和 WebUI
修正；任一组件缺失都会使构建失败，不会发布不完整的 SUSFS 包。

## 产物与安装

普通版产物只包含 ReSukiSU 内核。SUSFS 版还会包含匹配的
`WSA-SUSFS-2.3.0-Module-<架构>.zip` 模块和 SHA256 校验文件。

使用前请完全关闭 WSA，备份原文件，然后将对应架构的内核替换到：

`C:\Program Files\WSA_2407.40000.4.0_x64\Tools\kernel`

启动 WSA 后，在 KernelSU/ReSukiSU 管理器中安装同一 SUSFS 版本的模块，再重启
Android 子系统。x64 WSA 必须使用 x64 内核和 x64 SUSFS 模块；不要把 arm64
产物混用到 x64 安装中。

## SUSFS 组件与 WSA 适配

SUSFS 版本基于 Android 13 / Linux 5.15 上游实现，当前内核启用全部现行配置：

- SUS_PATH、SUS_MOUNT、SUS_KSTAT
- SPOOF_UNAME、SPOOF_CMDLINE_OR_BOOTCONFIG
- OPEN_REDIRECT、SUS_MAP
- SUSFS 日志和 KSU/SUSFS 符号隐藏
- AVC 日志伪装和 SUSFS 2.x userspace auto-umount 命令接口

WSA 专用适配包括：

- `/system/bin/su` 和 `/product/bin/su` 的虚拟路径查找与执行兼容；
- 修复 WSA 终端运行时中的 `argv[0]`，确保 `ksud` 选择正确的 su applet；
- 修复 ReSukiSU 旧版 GET_INFO ioctl 向 8 字节兼容缓冲区写入 12 字节的
  ABI 越界，使 Hybrid Mount 等旧接口客户端不会在检测 KernelSU 时崩溃；
- 适配 WSA 5.15 的 fanotify 回调 ABI；
- 使用 `vm_end` 兼容 WSA 缺失 `VMA_PAD_START` 的内核树；
- x64 使用原生 x86_64 `ksu_susfs`，避免 ARM64 工具经 Houdini 运行导致 WebUI
  查询为空；
- WebUI 禁用已知会触发部分 AMD 驱动崩溃的动画 Canvas 和 backdrop blur；
- 修正 SUSFS 2.x WebUI 的版本门槛，使 userspace auto-umount 与 non-su mount
  hide 控件正确显示。

## 已知版本差异

SUSFS 2.3.0 已废弃旧版 `AUTO_ADD_*`、内核 `TRY_UMOUNT`、`SUS_SU` 和 zygote
isolation 相关开关。它们不属于漏编；新版使用 userspace auto-umount、
`hide_sus_mnts_for_non_su_procs` 和 ReSukiSU supercall 替代。

x64 专用模块移除了上游自动更新入口，因为上游更新可能重新安装 ARM64
`ksu_susfs`。需要更新时应安装新的 WSA 专用模块产物。

## 固定版本

- ReSukiSU：`736d9fe8a66c18908e67cfaa4abf82c4326308aa`（35107）
- SUSFS：`bca0d2333c1a7d717e7278b019d7af7ba1d16005`（v2.3.0）
- SUSFS 模块：`d30974d4d6356cba1c322f8826b5fd7df904a4b9`（v1.5.2-R28）
- Android NDK：r27d（`27.3.13750724`）

## English

Provide manual hooks required for ResukiSU targeting WSA in the form of patch files.
Supply a workflow to automate prebuilt kernel compilation, which automatically pulls the latest ResukiSU release and completes kernel building.
User Instructions
You may download build artifacts from either the Actions page or Releases page, then replace the Tools/kernel file under your WSA installation directory with the downloaded file.
Note that not all Releases and Action builds are compatible for every user; please select the kernel version matching your environment.

## SUSFS builds

The workflow has an **Also build and publish the SUSFS variant** option.

- Disabled: build the standard ReSukiSU WSA kernel only.
- Enabled: build both the standard kernel and a SUSFS kernel in parallel, then
  upload/release both variants together.
- The SUSFS job also produces a matching WSA-compatible SUSFS module ZIP.

The SUSFS x64 module includes the native x86_64 `ksu_susfs` helper. Its install,
update and action scripts cannot replace that helper with the upstream ARM64
binary. The included WebUI disables the animated canvas/backdrop path that can
crash `WsaClient.exe` on affected AMD graphics drivers and exposes the SUSFS
2.x userspace auto-umount and non-su mount-hide controls. Automatic upstream
module updates are disabled for x64 because they would reinstall an ARM64-only
helper; update by installing a newer WSA-specific module artifact instead.
The workflow fails before upload if any required SUSFS config, module startup
script, native helper, or WSA WebUI compatibility marker is missing.

Pinned and tested revisions:

- ReSukiSU: `736d9fe8a66c18908e67cfaa4abf82c4326308aa` (version code 35107)
- SUSFS Android 13 / Linux 5.15: `bca0d2333c1a7d717e7278b019d7af7ba1d16005` (`v2.3.0`)
- SUSFS module: `d30974d4d6356cba1c322f8826b5fd7df904a4b9` (`v1.5.2-R28`)
- Android NDK: `r27d` (`27.3.13750724`)
