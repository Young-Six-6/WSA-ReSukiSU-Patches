# WSA-BakaSU-Patches

本项目为 WSA 5.15.104 内核迁移并维护 BakaSU 所需的手动钩子和 SUSFS 兼容补丁，并提供 GitHub Actions 工作流构建 x64 或 arm64 内核。

## 构建

在 GitHub Actions 页面打开现有的 Build WSA Kernel 5.15.104 (ReSukiSU)，点击 Run workflow，再选择 next 分支。该分支的工作流构建 BakaSU，可以设置以下选项。

- Target architecture：选择 x64 或 arm64。
- Also build and publish the SUSFS variant：关闭时构建 Manual Hook 标准版；开启时同时构建标准版和 SUSFS 版。
- Create one GitHub Release：可选地把本次所选架构和变体的产物发布到一个 Release。

BakaSU 把 Tracepoint、Manual Hook 和 SUSFS Hook 定义为互斥模式。工作流为标准版选择 Manual Hook，为 SUSFS 版选择 SUSFS Hook，并启用 BakaSU 当前 SUSFS 接口所需的 priority UID filter。

工作流锁定 BakaSU、SUSFS 和 SUSFS 模块的提交；上传前会核对源码提交、版本号、配置以及 SUSFS 模块文件。

## 产物与安装

标准版仅包含 BakaSU 内核。SUSFS 版还包含与架构匹配的 SUSFS 模块 ZIP 和 SHA256 校验文件。

使用前完全关闭 WSA 并备份原内核，然后把相应架构的内核替换到 WSA 安装目录下的 Tools/kernel。启动 WSA 后，在 BakaSU 管理器中安装对应的 SUSFS 模块（仅 SUSFS 版需要），再重启 Android 子系统。x64 WSA 使用 x64 内核和 x64 模块；不要混用 arm64 产物。

## WSA 兼容改动

- 为 /system/bin/su 和 /product/bin/su 添加受 allowlist 与 sucompat 开关控制的虚拟路径查找及执行处理；ksud 不存在时回退到 WSA 中可用的 /system/bin/sh。
- 在 Manual Hook 和 SUSFS Hook 路径中允许符合条件的 su 请求通过 no-su 快速拒绝检查；SUSFS 变体也会在内核路径上保留该例外。
- 执行 ksud 前把 argv[0] 设置为 su，供 ksud 选择 su applet。
- 在 init 第二阶段钩子缺失时延迟补做 SELinux 策略、SID 和 KSU credential 初始化。
- 修复旧版 GET_INFO ioctl 向兼容缓冲区多写入 features 字段的问题。
- 适配 WSA 5.15 的 fanotify 回调 ABI，并使用 vm_end 兼容该内核树缺失 VMA_PAD_START 的情况。
- SUSFS 变体基于上游 Android 13 / Linux 5.15 补丁，启用 SUS_PATH、SUS_MOUNT、SUS_KSTAT、SPOOF_UNAME、SPOOF_CMDLINE_OR_BOOTCONFIG、OPEN_REDIRECT、SUS_MAP、日志、符号隐藏及 priority UID filter。
- x64 SUSFS 模块使用原生 x86_64 ksu_susfs helper；WebUI 适配 WSA 图形驱动，并关闭会覆盖该 helper 的在线更新入口。

## 固定版本

- WSA 内核：android-lts/latte-2/5.15.104.4
- BakaSU：bc8224d043fda63dd9ebce2f9caa5466610f7286（version code 35283）
- SUSFS：c1d1da42b74771944207ec45aaceff9c57e84985（v2.4.0）
- SUSFS 模块：44ed418e486bdad4a0edfc016dc72e69a6c1be91（v1.5.2-R28）
- Android NDK：r27d（27.3.13750724）

## English

This repository carries WSA 5.15.104 compatibility patches for BakaSU and an Actions workflow for x64 or arm64 kernels. The workflow pins BakaSU, SUSFS, and the SUSFS module to immutable commits.

The standard kernel uses BakaSU Manual Hook. The optional SUSFS kernel uses BakaSU's mutually exclusive SUSFS Hook mode and enables the priority UID filter required by the current BakaSU integration.

WSA-specific changes cover virtual /system/bin/su and /product/bin/su paths (including a shell fallback when ksud is absent), no-su handling for authorized su execution, ksud argv[0], deferred SELinux setup, the legacy GET_INFO ABI, the WSA fanotify callback ABI, and VMA end compatibility. The SUSFS module is prepared with a native x86_64 helper and WSA-safe WebUI behavior.

Pinned revisions:

- BakaSU: bc8224d043fda63dd9ebce2f9caa5466610f7286 (version code 35283)
- SUSFS Android 13 / Linux 5.15: c1d1da42b74771944207ec45aaceff9c57e84985 (v2.4.0)
- SUSFS module: 44ed418e486bdad4a0edfc016dc72e69a6c1be91 (v1.5.2-R28)
- Android NDK: r27d (27.3.13750724)
